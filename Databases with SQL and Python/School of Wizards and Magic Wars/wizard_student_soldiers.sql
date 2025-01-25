/*
Stage 1: Adult and smart

Description
We need students to help defend the school. 
In this stage, find the 3rd-year students who 
have passed the courses of the semester with the best grades.

Objectives
Find students who are in 3rd grade and have 5 points for all their courses. 
The output should consist of the student names only in alphabetical order.

Hint:
Grade and semester columns show the year of the students. 
Result column shows the student's grade in the course. 
*/

SELECT 
    Students.name 
FROM   
    Students 
INNER JOIN Student_Subject 
    ON Students.student_ID = Student_Subject.student_id 
WHERE 
    Students.grade = 3
GROUP BY 
    Students.name
HAVING 
    MIN(Student_Subject.result) = 5
ORDER BY 
    Students.name;

/*
Stage 2: Best students

Description
The student efforts were insufficient to defend the school, so we need more students. 
To find them, you need to consider the student achievements. 
They need you to calculate them!

Objectives
Find four students with the most achievement points and 
list their names in alphabetical order with their scores. 
The student's year is not critical. 
The output should have only the name and the bonus point column. 
The output should be in descending order of the bonus point column.
*/

SELECT 
    Students.name,
    SUM(bonus) as [bonus point]
FROM 
    Students
INNER JOIN Student_Achievement
    ON Students.student_ID = Student_Achievement.student_ID
INNER JOIN Achievement
    ON Student_Achievement.achievement_id = Achievement.achievement_id
GROUP BY 
    name
ORDER BY 
    [bonus point] DESC
LIMIT 4;

/*
Stage 3: More students

Description
We've successfully repelled the attack, but the second wave is coming, and the students are tired. 
We need new students! Of course, it is you who must find these students.

Objectives
If the student's average is over 3.5 points for courses, output above average in the best column. 
Otherwise, print below average. Order the results in alphabetical order by name.
*/

SELECT 
    name,
    CASE 
        WHEN AVG(Student_Subject.result) > 3.5 THEN 'above average'
        ELSE 'below average'
        END AS best
FROM 
    Students
INNER JOIN Student_Subject 
    ON Students.student_id = Student_Subject.student_id 
GROUP BY 
    name
ORDER BY 
    name;

/*
Stage 4: Time to party

Description
We've done it! The attackers vanished. Let's hold a party at the school to commemorate this. 
The top winners of the department will be awarded. For this, they need your help again. 
You have to find the best students in the departments.

Objectives
You have to find the best students. The course averages of these students are above 4.5 points. 
The result should be in ascending order by name, with their names and which department they are in.
*/

SELECT 
    Students.name, 
    Department.department_name
FROM 
    Students
INNER JOIN Department
    ON Students.department_id = Department.department_id
WHERE 
    Students.student_id IN (
        SELECT 
            student_id
        FROM 
            Student_Subject
        GROUP BY 
            student_id
        HAVING 
            AVG(result) > 4.5)
ORDER BY 
    Students.name ASC;