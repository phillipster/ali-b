UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/aerospace-engineering'
 WHERE departmentID = 'AE';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/biomedical-engineering'
 WHERE departmentID = 'BMS';

UPDATE albert.department
   SET url = 'https://steinhardt.nyu.edu/academics/programs/culture-arts-media'
 WHERE departmentID = 'CAM';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/chemical-and-biological-engineering'
 WHERE departmentID = 'CBE';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/civil-and-urban-engineering'
 WHERE departmentID = 'CE';

UPDATE albert.department
   SET url = 'https://as.nyu.edu/departments/chemistry.html'
 WHERE departmentID = 'CM';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/experiential-learning/co-op'
 WHERE departmentID = 'CP';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/computer-science'
 WHERE departmentID = 'CS';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/integrated-design-and-media'
 WHERE departmentID = 'DM';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/electrical-and-computer-engineering'
 WHERE departmentID = 'ECE';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/general-engineering'
 WHERE departmentID = 'EG';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/calendars/final-exam-schedule'
 WHERE departmentID = 'EX';

UPDATE albert.department
   SET url = 'https://www.stern.nyu.edu/programs-admissions/undergraduate/academics/major-curriculum/finance'
 WHERE departmentID = 'FIN';

UPDATE albert.department
   SET url = 'https://steinhardt.nyu.edu/academics/programs/interdisciplinary-studies'
 WHERE departmentID = 'IS';

UPDATE albert.department
   SET url = 'https://math.nyu.edu/'
 WHERE departmentID = 'MA';

UPDATE albert.department
   SET url = 'https://steinhardt.nyu.edu/academics/programs/media-studies'
 WHERE departmentID = 'MD';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/departments/mechanical-and-aerospace-engineering'
 WHERE departmentID = 'ME';

UPDATE albert.department
   SET url = 'https://www.stern.nyu.edu/programs-admissions/undergraduate/academics/major-curriculum/management'
 WHERE departmentID = 'MG';

UPDATE albert.department
   SET url = 'https://as.nyu.edu/departments/physics.html'
 WHERE departmentID = 'PH';

UPDATE albert.department
   SET url = 'https://as.nyu.edu/student-life/resources/pre-health-advising.html'
 WHERE departmentID = 'PHP';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/research/robotics'
 WHERE departmentID = 'ROB';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/current-students/student-life'
 WHERE departmentID = 'SL';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/research'
 WHERE departmentID = 'STS';

UPDATE albert.department
   SET url = 'https://steinhardt.nyu.edu/academics/programs/technology-culture-and-society'
 WHERE departmentID = 'TCS';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/undergraduate'
 WHERE departmentID = 'UGA';

UPDATE albert.department
   SET url = 'https://as.nyu.edu/academics/undergraduate-degree-programs/urban-studies.html'
 WHERE departmentID = 'URB';

UPDATE albert.department
   SET url = 'https://engineering.nyu.edu/academics/experiential-learning/vertically-integrated-projects'
 WHERE departmentID = 'VIP';

create table campus
(
    campusID    int          not null
        primary key,
    campus_name varchar(100) null,
    country     varchar(100) null,
    zip_code    varchar(100) null,
    image_src   varchar(150) null,
    url         varchar(100) null
);

INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (1, 'Brooklyn', 'United States', '11201', '../static/images/tandon.jpg', 'https://engineering.nyu.edu/admissions/location');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (2, 'Manhattan', 'United States', '10003', '../static/images/manhattan.jpeg', 'https://www.nyu.edu/new-york.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (3, 'Shanghai', 'China', '200124', '../static/images/shanghai.jpg', 'https://www.nyu.edu/shanghai.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (4, 'Abu Dhabi', 'United Arab Emirates', '129188', '../static/images/abu_dhabi.jpg', 'https://www.nyu.edu/abu-dhabi.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (5, 'Accra', 'Ghana', '', '../static/images/accra.png', 'https://www.nyu.edu/accra.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (6, 'Berlin', 'Germany', '10435', '../static/images/berlin.webp', 'https://www.nyu.edu/berlin.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (7, 'Buenos Aires', 'Argentina', 'C1425', '../static/images/buenos_aires.jpg', 'https://www.nyu.edu/buenos-aires.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (8, 'Florence', 'Italy', '50139', '../static/images/florence.jpg', 'https://www.nyu.edu/florence.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (9, 'London', 'United Kingdom', 'WC1B 3RA', '../static/images/london.jpg', 'https://www.nyu.edu/london.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (10, 'Los Angeles', 'United States', '90036', '../static/images/los_angeles.png', 'https://www.nyu.edu/los-angeles.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (11, 'Madrid', 'Spain', '28004', '../static/images/madrid.png', 'https://www.nyu.edu/madrid.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (12, 'Paris', 'France', '75005', '../static/images/paris.png', 'https://www.nyu.edu/paris.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (13, 'Prague', 'Czechia', '120 00', '../static/images/prague.jpg', 'https://www.nyu.edu/prague.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (14, 'Sydney', 'Australia', '2000', '../static/images/sydney.jpg', 'https://www.nyu.edu/sydney.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (15, 'Tel Aviv', 'Israel', '62001', '../static/images/tel_aviv.jpg', 'https://www.nyu.edu/telaviv.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (16, 'Tulsa', 'United States', '74103', '../static/images/tulsa.png', 'https://www.nyu.edu/tulsa.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (17, 'Washington, DC', 'United States', '20005', '../static/images/dc.jpg', 'https://www.nyu.edu/washington-dc.html');
INSERT INTO albert.campus (campusID, campus_name, country, zip_code, image_src, url) VALUES (18, 'ePoly', 'United States', '', null, null);

create table degree
(
    degreeID    int           not null
        primary key,
    degree_name varchar(1000) null,
    schoolID    varchar(10)   null,
    url         varchar(1000) null,
    description varchar(1000) null,
    constraint degree_ibfk_1
        foreign key (schoolID) references school (schoolID)
);

create index schoolID
    on degree (schoolID);

INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (1, 'Applied Physics', 'Y', 'https://engineering.nyu.edu/programs/applied-physics-bs', 'Applied Physics is devoted to the study and understanding of nature. Considered the most fundamental science, it deals with the constituents, properties, and evolution of the entire universe, from the smallest subatomic particles to the largest galaxies.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (2, 'Biomolecular Science', 'Y', 'https://engineering.nyu.edu/academics/programs/biomolecular-science-bs', 'Scientists working at the interface between biology and chemistry create big changes while working on the cellular and molecular level.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (3, 'Business and Technology Management', 'Y', 'https://engineering.nyu.edu/academics/programs/business-and-technology-management-bs', 'Oriented toward current and future high growth arenas, the Business and Technology Management (BTM) trains business leaders of tomorrow. You’ll become deeply familiar with technology and innovation and work in diverse venues.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (4, 'Chemical and Biomolecular Engineering', 'Y', 'https://engineering.nyu.edu/academics/programs/business-and-technology-management-bs', 'As a chemical and biomolecular engineer, you\'ll become part of a field that has contributed to the development of virtually every material common to modern life and emerging technologies.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (5, 'Civil Enginering', 'Y', 'https://engineering.nyu.edu/academics/programs/civil-engineering-bs', 'Civil engineering includes everything from the design and construction of buildings, bridges, and roads to securing our water resources and preparing for pressing environmental and social challenges.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (6, 'Computer Engineering', 'Y', 'https://engineering.nyu.edu/academics/programs/computer-engineering-bs', 'Computer engineers develop products that touch nearly every part of our lives, from sending e-mails from cell phones to reconstructing genomes. That’s just the kind of invention & innovation the School of Engineering encourages.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (7, 'Computer Science', 'Y', 'https://engineering.nyu.edu/academics/programs/computer-science-bs', 'Computer science focuses on designing, building, and using the computers and systems that we interact with every day — from iPhones to the complex databases in banks and hospitals.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (8, 'Electrical and Computer Engineering', 'Y', 'https://engineering.nyu.edu/academics/programs/electrical-engineering-and-computer-engineering-bs', 'Electrical Engineering and Computer Engineering are both extremely pertinent in today\'s high technology and global world, and this program gives students opportunities to garner knowledge from both disciplines.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (9, 'Electrical Engineering', 'Y', 'https://engineering.nyu.edu/academics/programs/electrical-engineering-bs', 'From the subway systems beneath our cities to the HD televisions on our walls, innovations by electrical engineers touch every aspect of modern life, but new challenges await the electrical engineers of tomorrow.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (10, 'Integrated Design and Media', 'Y', 'https://engineering.nyu.edu/academics/programs/integrated-design-media-bs', 'Our Bachelor of Science Integrated Design & Media (IDM) program centers around the IDM core, a suite of courses that focus on the four areas of Image, Sound, Narrative, and Interactivity.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (11, 'Mathematics', 'Y', 'https://engineering.nyu.edu/academics/programs/mathematics-bs', 'Mathematics forms the backbone of scientific fields, like physics, engineering, and computer science. With a firm grasp of mathematics, you’ll have the foundation to launch explorations of related disciplines.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (12, 'Mathematics and Physics', 'Y', 'https://engineering.nyu.edu/academics/programs/mathematics-and-physics-bs', 'Mathematics has applications to nearly every branch of science and engineering, and advances in physics — for example, those in electromagnetism and thermodynamics — often resonate deeply with mathematics.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (13, 'Mechanical Engineering', 'Y', 'https://engineering.nyu.edu/academics/programs/mechanical-engineering-bs', 'Mechanical engineering builds the physical systems and devices that define modern society — everything from air conditioning to automobiles, robots to power plants, artificial limbs to escalators.');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (14, 'Hellenic Studies', 'A', 'https://as.nyu.edu/departments/hellenic.html', 'Hellenic Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (15, 'History', 'A', 'https://as.nyu.edu/departments/history.html', 'History');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (16, 'International Relations', 'A', 'https://cas.nyu.edu/academic-programs/bulletin/departments-and-programs/major-in-international-relations/program-of-study-cas-bulletin.html', 'International Relations');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (17, 'Italian', 'A', 'https://as.nyu.edu/departments/italian/undergraduate.html', 'Italian');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (18, 'Italian and Linguistics', 'A', 'https://as.nyu.edu/departments/linguistics.html', 'Italian and Linguistics');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (19, 'Journalism', 'A', 'https://www.journalism.nyu.edu/', 'Journalism');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (20, 'Language and Mind', 'A', 'https://as.nyu.edu/departments/lamd.html', 'Language and Mind');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (21, 'Latin American and Caribbean Studies', 'A', 'https://as.nyu.edu/research-centers/clacs.html', 'Latin American and Caribbean Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (22, 'Latino Studies', 'A', 'https://as.nyu.edu/departments/latinostudies.html', 'Latino Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (23, 'Linguistics', 'A', 'https://as.nyu.edu/departments/linguistics.html', 'Linguistics');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (24, 'Mathematics', 'A', 'https://www.math.nyu.edu/', 'Mathematics,');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (25, 'Mathematics and Computer Science', 'A', 'https://www.math.nyu.edu/', 'Mathematics and Computer Science');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (26, 'Medieval and Renaissance Studies', 'A', 'https://as.nyu.edu/research-centers/marc.html', 'Medieval and Renaissance Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (27, 'Metropolitan Studies', 'A', 'https://as.nyu.edu/departments/metropolitanstudies.html', 'Metropolitan Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (28, 'Middle Eastern Studies', 'A', 'https://as.nyu.edu/departments/meis.html', 'Middle Eastern Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (29, 'Music', 'A', 'https://as.nyu.edu/departments/music.html', 'Music');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (30, 'Neural Science', 'A', 'http://www.cns.nyu.edu/', 'Neural Science');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (31, 'Philosophy', 'A', 'https://as.nyu.edu/departments/philosophy.html', 'Philosophy');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (32, 'Physics', 'A', 'https://as.nyu.edu/departments/physics.html', 'Physics,');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (33, 'Politics', 'A', 'https://as.nyu.edu/departments/politics.html', 'Politics');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (34, 'Psychology', 'A', 'http://psych.nyu.edu/psychology.html', 'Psychology');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (35, 'Public Policy', 'A', 'http://wagner.nyu.edu/education/undergraduate/major', 'Public Policy');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (36, 'Religious Studies', 'A', 'https://as.nyu.edu/departments/religiousstudies.html', 'Religious Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (37, 'Romance Languages', 'A', 'https://as.nyu.edu/departments/spanish.html', 'Romance Languages');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (38, 'Russian and Slavic Studies', 'A', 'https://as.nyu.edu/departments/russianslavic.html', 'Russian and Slavic Studies');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (39, 'Social and Cultural Analysis', 'A', 'https://as.nyu.edu/departments/sca.html', 'Social and Cultural Analysis');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (40, 'Sociology', 'A', 'https://as.nyu.edu/departments/sociology.html', 'Sociology');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (41, 'Spanish and Linguistics', 'A', 'https://as.nyu.edu/departments/linguistics.html', 'Spanish and Linguistics');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (42, 'Spanish and Portuguese', 'A', 'https://as.nyu.edu/departments/spanish.html', 'Spanish and Portuguese');
INSERT INTO albert.degree (degreeID, degree_name, schoolID, url, description) VALUES (43, 'Urban Design and Architecture Studies', 'A', 'https://as.nyu.edu/departments/arthistory/programs/undergraduate/urban-design-and-architecture-studies.html', 'Urban Design and Architecture Studies');
