#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <map>
#include <algorithm>
#include <iomanip>
#include <memory>
using namespace std;

// ─────────────────────────────────────────
// CLASSES
// ─────────────────────────────────────────
class Student {
public:
    string roll, name, gender, cnic, contact, father;
};

class Course {
public:
    string semester, code, name;
    int th_credits, lab_credits;
    string teacher;

    int total_credits() const { return th_credits + lab_credits; }
};

class Marks {
public:
    string roll, semester, course;
    int q1, q2, mid, final_exam, assign;

    int total() const {
        return q1 + q2 + mid + final_exam + assign;
    }

    float percentage() const {
        return (total() / 100.0f) * 100.0f;
    }

    string grade() const {
        float p = percentage();
        if (p >= 85) return "A+";
        if (p >= 80) return "A";
        if (p >= 75) return "B+";
        if (p >= 70) return "B";
        if (p >= 65) return "C+";
        if (p >= 60) return "C";
        if (p >= 55) return "D+";
        if (p >= 50) return "D";
        return "F";
    }

    float grade_points() const {
        string g = grade();
        if (g == "A+") return 4.0f;
        if (g == "A")  return 4.0f;
        if (g == "B+") return 3.5f;
        if (g == "B")  return 3.0f;
        if (g == "C+") return 2.5f;
        if (g == "C")  return 2.0f;
        if (g == "D+") return 1.5f;
        if (g == "D")  return 1.0f;
        return 0.0f;
    }
};

const Course* find_course(const vector<Course>& courses,
                          const string& code,
                          const string& semester);

const Student* find_student(const vector<Student>& students,
                            const string& roll);

pair<string,int> course_info(const vector<Course>& courses,
                             const string& code,
                             const string& semester);

void save_marks(const string& file, const vector<Marks>& marks);
void save_students(const string& file, const vector<Student>& students);

class GradeCalculator {
public:
    virtual ~GradeCalculator() = default;
    virtual float calculate(const string& roll,
                            const string& semester,
                            const vector<Marks>& all_marks,
                            const vector<Course>& courses) const = 0;
};

class GpaCalculator : public GradeCalculator {
public:
    float calculate(const string& roll,
                    const string& semester,
                    const vector<Marks>& all_marks,
                    const vector<Course>& courses) const override {
        float total_points = 0;
        int total_credits = 0;
        for (auto const& m : all_marks) {
            if (m.roll != roll || m.semester != semester) continue;
            if (auto course = find_course(courses, m.course, semester)) {
                int cr = course->total_credits();
                total_points += m.grade_points() * cr;
                total_credits += cr;
            }
        }
        return total_credits == 0 ? 0.0f : total_points / total_credits;
    }
};

class CgpaCalculator : public GradeCalculator {
public:
    float calculate(const string& roll,
                    const string& /*semester*/,
                    const vector<Marks>& all_marks,
                    const vector<Course>& courses) const override {
        float total_points = 0;
        int total_credits = 0;
        for (auto const& m : all_marks) {
            if (m.roll != roll) continue;
            if (auto course = find_course(courses, m.course, m.semester)) {
                int cr = course->total_credits();
                total_points += m.grade_points() * cr;
                total_credits += cr;
            }
        }
        return total_credits == 0 ? 0.0f : total_points / total_credits;
    }
};

class Command {
public:
    string name;
    int minArgs;
    Command(const string& commandName, int minArgsCount)
        : name(commandName), minArgs(minArgsCount) {}
    virtual ~Command() = default;
    bool matches(const string& cmd, int argc) const {
        return cmd == name && argc >= minArgs;
    }
    virtual void execute(int argc, char* argv[], const string& base,
                         vector<Student>& students,
                         vector<Course>& courses,
                         vector<Marks>& marks) const = 0;
};

class GetStudentsCommand : public Command {
public:
    GetStudentsCommand() : Command("GET_STUDENTS", 2) {}
    void execute(int, char*[], const string&,
                 vector<Student>& students,
                 vector<Course>& courses,
                 vector<Marks>& marks) const override {
        CgpaCalculator cgpaCalc;
        for (auto& s : students) {
            float cgpa = cgpaCalc.calculate(s.roll, "", marks, courses);
            cout << s.roll << "|" << s.name << "|" << s.gender
                 << "|" << s.contact << "|" << s.father
                 << "|" << fixed << setprecision(2) << cgpa << "\n";
        }
    }
};

class GetMarksCommand : public Command {
public:
    GetMarksCommand() : Command("GET_MARKS", 4) {}
    void execute(int argc, char* argv[], const string&,
                 vector<Student>&,
                 vector<Course>&,
                 vector<Marks>& marks) const override {
        string roll = argv[2];
        string sem = argv[3];
        for (auto& m : marks) {
            if (m.roll == roll && m.semester == sem) {
                cout << m.course << "|" << m.q1 << "|" << m.q2
                     << "|" << m.mid << "|" << m.final_exam
                     << "|" << m.assign << "|" << m.total()
                     << "|" << m.grade() << "|"
                     << fixed << setprecision(1) << m.percentage() << "\n";
            }
        }
    }
};

class GetGpaCommand : public Command {
public:
    GetGpaCommand() : Command("GET_GPA", 3) {}
    void execute(int argc, char* argv[], const string&,
                 vector<Student>&,
                 vector<Course>& courses,
                 vector<Marks>& marks) const override {
        string roll = argv[2];
        GpaCalculator gpaCalc;
        CgpaCalculator cgpaCalc;
        float gpa1 = gpaCalc.calculate(roll, "SEM1", marks, courses);
        float gpa2 = gpaCalc.calculate(roll, "SEM2", marks, courses);
        float cgpa = cgpaCalc.calculate(roll, "", marks, courses);
        cout << fixed << setprecision(2)
             << gpa1 << "|" << gpa2 << "|" << cgpa << "\n";
    }
};

class UpdateMarksCommand : public Command {
public:
    UpdateMarksCommand() : Command("UPDATE_MARKS", 10) {}
    void execute(int argc, char* argv[], const string& base,
                 vector<Student>&,
                 vector<Course>&,
                 vector<Marks>& marks) const override {
        string roll = argv[2];
        string sem = argv[3];
        string course = argv[4];
        int q1 = stoi(argv[5]);
        int q2 = stoi(argv[6]);
        int mid = stoi(argv[7]);
        int fin = stoi(argv[8]);
        int asgn = stoi(argv[9]);
        bool found = false;
        for (auto& m : marks) {
            if (m.roll == roll && m.semester == sem && m.course == course) {
                m.q1 = q1; m.q2 = q2; m.mid = mid;
                m.final_exam = fin; m.assign = asgn;
                found = true;
                break;
            }
        }
        if (!found) {
            Marks nm;
            nm.roll = roll; nm.semester = sem; nm.course = course;
            nm.q1 = q1; nm.q2 = q2; nm.mid = mid;
            nm.final_exam = fin; nm.assign = asgn;
            marks.push_back(nm);
        }
        save_marks(base + "marks.txt", marks);
        cout << "OK\n";
    }
};

class AddStudentCommand : public Command {
public:
    AddStudentCommand() : Command("ADD_STUDENT", 7) {}
    void execute(int argc, char* argv[], const string& base,
                 vector<Student>& students,
                 vector<Course>&,
                 vector<Marks>&) const override {
        Student s;
        s.roll = argv[2]; s.name = argv[3]; s.gender = argv[4];
        s.cnic = argv[5]; s.contact = argv[6];
        s.father = argc >= 8 ? argv[7] : "";
        students.push_back(s);
        save_students(base + "students.txt", students);
        cout << "OK\n";
    }
};

class UpdateStudentCommand : public Command {
public:
    UpdateStudentCommand() : Command("UPDATE_STUDENT", 7) {}
    void execute(int argc, char* argv[], const string& base,
                 vector<Student>& students,
                 vector<Course>&,
                 vector<Marks>&) const override {
        string roll = argv[2];
        for (auto& s : students) {
            if (s.roll == roll) {
                s.name = argv[3]; s.gender = argv[4];
                s.cnic = argv[5]; s.contact = argv[6];
                if (argc >= 8) s.father = argv[7];
                break;
            }
        }
        save_students(base + "students.txt", students);
        cout << "OK\n";
    }
};

class DeleteStudentCommand : public Command {
public:
    DeleteStudentCommand() : Command("DELETE_STUDENT", 3) {}
    void execute(int argc, char* argv[], const string& base,
                 vector<Student>& students,
                 vector<Course>&,
                 vector<Marks>& marks) const override {
        string roll = argv[2];
        students.erase(
            remove_if(students.begin(), students.end(),
                      [&roll](const Student& s){ return s.roll == roll; }),
            students.end()
        );
        marks.erase(
            remove_if(marks.begin(), marks.end(),
                      [&roll](const Marks& m){ return m.roll == roll; }),
            marks.end()
        );
        save_students(base + "students.txt", students);
        save_marks(base + "marks.txt", marks);
        cout << "OK\n";
    }
};

class GetStatsCommand : public Command {
public:
    GetStatsCommand() : Command("GET_STATS", 2) {}
    void execute(int, char*[], const string&,
                 vector<Student>& students,
                 vector<Course>& courses,
                 vector<Marks>& marks) const override {
        CgpaCalculator cgpaCalc;
        int total = students.size();
        float sum_cgpa = 0;
        float top_cgpa = 0;
        string top_name;
        int passing = 0;
        for (auto& s : students) {
            float cgpa = cgpaCalc.calculate(s.roll, "", marks, courses);
            sum_cgpa += cgpa;
            if (cgpa > top_cgpa) {
                top_cgpa = cgpa;
                top_name = s.name;
            }
            if (cgpa >= 2.0f) passing++;
        }
        float avg_cgpa = total > 0 ? sum_cgpa / total : 0;
        map<string, pair<float,int>> sub_avgs;
        for (auto& m : marks) {
            if (m.semester != "SEM2") continue;
            sub_avgs[m.course].first += m.percentage();
            sub_avgs[m.course].second += 1;
        }
        cout << "TOTAL:" << total << "\n";
        cout << fixed << setprecision(2);
        cout << "AVG_CGPA:" << avg_cgpa << "\n";
        cout << "TOP_CGPA:" << top_cgpa << "\n";
        cout << "TOP_NAME:" << top_name << "\n";
        cout << "PASSING:" << passing << "\n";
        for (auto& kv : sub_avgs) {
            float avg = kv.second.first / kv.second.second;
            cout << "SUB:" << kv.first << ":"
                 << fixed << setprecision(1) << avg << "\n";
        }
    }
};

class GetResultCommand : public Command {
public:
    GetResultCommand() : Command("GET_RESULT", 3) {}
    void execute(int argc, char* argv[], const string&,
                 vector<Student>& students,
                 vector<Course>& courses,
                 vector<Marks>& marks) const override {
        string roll = argv[2];
        auto st = find_student(students, roll);
        if (!st) { cout << "NOT_FOUND\n"; return; }
        cout << "NAME:" << st->name << "\n";
        cout << "ROLL:" << st->roll << "\n";
        cout << "FATHER:" << st->father << "\n";
        GpaCalculator gpaCalc;
        CgpaCalculator cgpaCalc;
        for (auto& sem : vector<string>{"SEM1","SEM2"}) {
            float gpa = gpaCalc.calculate(roll, sem, marks, courses);
            cout << "SEM:" << sem << ":GPA:"
                 << fixed << setprecision(2) << gpa << "\n";
            for (auto& m : marks) {
                if (m.roll != roll || m.semester != sem) continue;
                auto [cname, cr] = course_info(courses, m.course, sem);
                cout << "MARKS:" << sem << "|" << m.course << "|"
                     << cname << "|" << cr << "|"
                     << m.q1 << "|" << m.q2 << "|" << m.mid << "|"
                     << m.final_exam << "|" << m.assign << "|"
                     << m.total() << "|" << m.grade() << "|"
                     << fixed << setprecision(1) << m.percentage() << "\n";
            }
        }
        float cgpa = cgpaCalc.calculate(roll, "", marks, courses);
        cout << "CGPA:" << fixed << setprecision(2) << cgpa << "\n";
    }
};

// ─────────────────────────────────────────
// FILE READING FUNCTIONS
// ─────────────────────────────────────────
vector<string> split(const string& s, char delim) {
    vector<string> parts;
    stringstream ss(s);
    string token;
    while (getline(ss, token, delim))
        parts.push_back(token);
    return parts;
}

vector<Student> load_students(const string& file) {
    vector<Student> students;
    ifstream fin(file);
    string line;
    while (getline(fin, line)) {
        if (line.empty() || line[0] == '#') continue;
        auto p = split(line, '|');
        if (p.size() < 6) continue;
        Student s;
        s.roll = p[0]; s.name = p[1]; s.gender = p[2];
        s.cnic = p[3]; s.contact = p[4]; s.father = p[5];
        students.push_back(s);
    }
    return students;
}

vector<Course> load_courses(const string& file) {
    vector<Course> courses;
    ifstream fin(file);
    string line;
    while (getline(fin, line)) {
        if (line.empty() || line[0] == '#') continue;
        auto p = split(line, '|');
        if (p.size() < 6) continue;
        Course c;
        c.semester = p[0]; c.code = p[1]; c.name = p[2];
        c.th_credits = stoi(p[3]); c.lab_credits = stoi(p[4]);
        c.teacher = p[5];
        courses.push_back(c);
    }
    return courses;
}

vector<Marks> load_marks(const string& file) {
    vector<Marks> marks;
    ifstream fin(file);
    string line;
    while (getline(fin, line)) {
        if (line.empty() || line[0] == '#') continue;
        auto p = split(line, '|');
        if (p.size() < 8) continue;
        Marks m;
        m.roll = p[0]; m.semester = p[1]; m.course = p[2];
        m.q1 = stoi(p[3]); m.q2 = stoi(p[4]);
        m.mid = stoi(p[5]); m.final_exam = stoi(p[6]);
        m.assign = stoi(p[7]);
        marks.push_back(m);
    }
    return marks;
}

const Course* find_course(const vector<Course>& courses,
                          const string& code,
                          const string& semester) {
    for (auto const& c : courses) {
        if (c.code == code && c.semester == semester)
            return &c;
    }
    return nullptr;
}

const Student* find_student(const vector<Student>& students,
                            const string& roll) {
    for (auto const& s : students) {
        if (s.roll == roll) return &s;
    }
    return nullptr;
}

pair<string,int> course_info(const vector<Course>& courses,
                             const string& code,
                             const string& semester) {
    if (auto course = find_course(courses, code, semester))
        return {course->name, course->total_credits()};
    return {code, 0};
}

float calc_gpa(const string& roll, const string& semester,
               const vector<Marks>& all_marks,
               const vector<Course>& courses) {
    float total_points = 0;
    int   total_credits = 0;

    for (auto const& m : all_marks) {
        if (m.roll != roll || m.semester != semester) continue;
        if (auto course = find_course(courses, m.course, semester)) {
            int cr = course->total_credits();
            total_points += m.grade_points() * cr;
            total_credits += cr;
        }
    }
    return total_credits == 0 ? 0.0f : total_points / total_credits;
}

float calc_cgpa(const string& roll,
                const vector<Marks>& all_marks,
                const vector<Course>& courses) {
    float total_points = 0;
    int   total_credits = 0;

    for (auto const& m : all_marks) {
        if (m.roll != roll) continue;
        if (auto course = find_course(courses, m.course, m.semester)) {
            int cr = course->total_credits();
            total_points += m.grade_points() * cr;
            total_credits += cr;
        }
    }
    return total_credits == 0 ? 0.0f : total_points / total_credits;
}

// ─────────────────────────────────────────
// SAVE MARKS
// ─────────────────────────────────────────
void save_marks(const string& file, const vector<Marks>& marks) {
    ofstream fout(file);
    fout << "# Marks Data\n";
    fout << "# Format: ROLL|SEMESTER|COURSE|Q1|Q2|MID|FINAL|ASSIGN\n";
    for (auto& m : marks) {
        fout << m.roll << "|" << m.semester << "|" << m.course
             << "|" << m.q1 << "|" << m.q2 << "|" << m.mid
             << "|" << m.final_exam << "|" << m.assign << "\n";
    }
}

void save_students(const string& file, const vector<Student>& students) {
    ofstream fout(file);
    fout << "# BSc Computer Engineering 2025\n";
    fout << "# Format: ROLL|NAME|GENDER|CNIC|CONTACT|FATHER_NAME\n\n";
    for (auto& s : students) {
        fout << s.roll << "|" << s.name << "|" << s.gender
             << "|" << s.cnic << "|" << s.contact << "|" << s.father << "\n";
    }
}

// ─────────────────────────────────────────
// MAIN — Command line interface for Python
// ─────────────────────────────────────────
int main(int argc, char* argv[]) {
    string base = "data/";
    auto students = load_students(base + "students.txt");
    auto courses  = load_courses(base + "courses.txt");
    auto marks    = load_marks(base + "marks.txt");

    if (argc < 2) {
        // Default: print stats
        cout << "STUDENTS:" << students.size() << "\n";
        return 0;
    }

    string cmd = argv[1];
    vector<unique_ptr<Command>> commands;
    commands.push_back(make_unique<GetStudentsCommand>());
    commands.push_back(make_unique<GetMarksCommand>());
    commands.push_back(make_unique<GetGpaCommand>());
    commands.push_back(make_unique<UpdateMarksCommand>());
    commands.push_back(make_unique<AddStudentCommand>());
    commands.push_back(make_unique<UpdateStudentCommand>());
    commands.push_back(make_unique<DeleteStudentCommand>());
    commands.push_back(make_unique<GetStatsCommand>());
    commands.push_back(make_unique<GetResultCommand>());

    for (auto const& command : commands) {
        if (command->matches(cmd, argc)) {
            command->execute(argc, argv, base, students, courses, marks);
            return 0;
        }
    }

    return 0;
}
