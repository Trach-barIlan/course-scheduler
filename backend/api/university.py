from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Dict, Any, Optional
from auth.routes import get_current_user

university_router = APIRouter(prefix="/api/university", tags=["university"])

# Data remains the same, just keeping the structure for the router
UNIVERSITIES = {
    # United States Universities
    'harvard': {
        'id': 'harvard',
        'name': 'Harvard University',
        'location': 'Cambridge, MA',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://courses.harvard.edu',
        'logo': 'https://1000logos.net/wp-content/uploads/2017/02/Harvard-Logo.png',
        'departments': ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Economics']
    },
    'mit': {
        'id': 'mit', 
        'name': 'Massachusetts Institute of Technology',
        'location': 'Cambridge, MA',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://student.mit.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2022/01/MIT-Logo.png',
        'departments': ['Electrical Engineering', 'Computer Science', 'Mathematics', 'Physics', 'Mechanical Engineering']
    },
    'stanford': {
        'id': 'stanford',
        'name': 'Stanford University',
        'location': 'Stanford, CA',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://explorecourses.stanford.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/06/Stanford-Logo.png',
        'departments': ['Computer Science', 'Engineering', 'Business', 'Medicine', 'Law']
    },
    'yale': {
        'id': 'yale',
        'name': 'Yale University',
        'location': 'New Haven, CT',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://courses.yale.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/05/Yale-Logo.png',
        'departments': ['Liberal Arts', 'Computer Science', 'Economics', 'History', 'Psychology']
    },
    'princeton': {
        'id': 'princeton',
        'name': 'Princeton University',
        'location': 'Princeton, NJ',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://registrar.princeton.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/06/Princeton-Logo.png',
        'departments': ['Computer Science', 'Economics', 'Physics', 'Mathematics', 'Political Science']
    },
    'columbia': {
        'id': 'columbia',
        'name': 'Columbia University',
        'location': 'New York, NY',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://bulletins.columbia.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/06/Columbia-Logo.png',
        'departments': ['Computer Science', 'Journalism', 'Business', 'Medicine', 'Law']
    },
    'berkeley': {
        'id': 'berkeley',
        'name': 'UC Berkeley',
        'location': 'Berkeley, CA',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://classes.berkeley.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/05/UC-Berkeley-Logo.png',
        'departments': ['Computer Science', 'Engineering', 'Business', 'Biology', 'Chemistry']
    },
    'ucla': {
        'id': 'ucla',
        'name': 'UCLA',
        'location': 'Los Angeles, CA',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://sa.ucla.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/05/UCLA-Logo.png',
        'departments': ['Computer Science', 'Film Studies', 'Medicine', 'Business', 'Psychology']
    },
    'nyu': {
        'id': 'nyu',
        'name': 'New York University',
        'location': 'New York, NY',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://albert.nyu.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2021/09/New-York-University-Logo.png',
        'departments': ['Computer Science', 'Business', 'Film', 'Arts', 'Medicine']
    },
    'chicago': {
        'id': 'chicago',
        'name': 'University of Chicago',
        'location': 'Chicago, IL',
        'country': 'USA',
        'hasApi': False,
        'catalogUrl': 'https://classes.uchicago.edu',
        'logo': 'https://logos-world.net/wp-content/uploads/2020/06/University-of-Chicago-Logo.png',
        'departments': ['Economics', 'Computer Science', 'Physics', 'Mathematics', 'Business']
    },
    'hebrew-university': {
        'id': 'hebrew-university',
        'name': 'Hebrew University of Jerusalem', 
        'location': 'Jerusalem',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://shnaton.huji.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/Hebrew_University_Logo.svg/1200px-Hebrew_University_Logo.svg.png',
        'departments': ['Computer Science', 'Mathematics', 'Physics', 'Biology', 'Medicine']
    },
    'technion': {
        'id': 'technion',
        'name': 'Technion - Israel Institute of Technology',
        'location': 'Haifa',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://ug.technion.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/81/Technion_Israel_Institute_of_Technology_logo.svg/1200px-Technion_Israel_Institute_of_Technology_logo.svg.png',
        'departments': ['Computer Science', 'Electrical Engineering', 'Mechanical Engineering', 'Aerospace Engineering', 'Chemical Engineering']
    },
    'tel-aviv': {
        'id': 'tel-aviv',
        'name': 'Tel Aviv University',
        'location': 'Tel Aviv',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.tau.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Tel_Aviv_University_Logo.svg/1200px-Tel_Aviv_University_Logo.svg.png',
        'departments': ['Computer Science', 'Business', 'Medicine', 'Law', 'Arts']
    },
    'weizmann': {
        'id': 'weizmann',
        'name': 'Weizmann Institute of Science',
        'location': 'Rehovot',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.weizmann.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Weizmann_Institute_of_Science_logo.svg/1200px-Weizmann_Institute_of_Science_logo.svg.png',
        'departments': ['Physics', 'Chemistry', 'Biology', 'Mathematics', 'Computer Science']
    },
    'ben-gurion': {
        'id': 'ben-gurion',
        'name': 'Ben-Gurion University of the Negev',
        'location': 'Beer Sheva',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.bgu.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Ben-Gurion_University_of_the_Negev_logo.svg/1200px-Ben-Gurion_University_of_the_Negev_logo.svg.png',
        'departments': ['Computer Science', 'Engineering', 'Medicine', 'Desert Studies', 'Cybersecurity']
    },
    'haifa': {
        'id': 'haifa',
        'name': 'University of Haifa',
        'location': 'Haifa',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.haifa.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/University_of_Haifa_logo.svg/1200px-University_of_Haifa_logo.svg.png',
        'departments': ['Computer Science', 'Education', 'Social Work', 'Political Science', 'International Relations']
    },
    'idc-herzliya': {
        'id': 'idc-herzliya',
        'name': 'Reichman University (IDC Herzliya)',
        'location': 'Herzliya',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.runi.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Reichman_University_logo.svg/1200px-Reichman_University_logo.svg.png',
        'departments': ['Computer Science', 'Business', 'Communications', 'Law', 'Government']
    },
    'open-university': {
        'id': 'open-university',
        'name': 'Open University of Israel',
        'location': 'Ra\'anana',
        'country': 'Israel',
        'hasApi': False,
        'catalogUrl': 'https://www.openu.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3f/Open_University_of_Israel_logo.svg/1200px-Open_University_of_Israel_logo.svg.png',
        'departments': ['Computer Science', 'Mathematics', 'Social Sciences', 'Education', 'Management']
    },
    'bar-ilan': {
        'id': 'bar-ilan',
        'name': 'Bar-Ilan University',
        'location': 'Ramat Gan',
        'country': 'Israel',
        'hasApi': True,
        'catalogUrl': 'https://courses.biu.ac.il',
        'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f4/Bar-Ilan_University_logo.svg/1200px-Bar-Ilan_University_logo.svg.png',
        'departments': ['Computer Science', 'Mathematics', 'Physics', 'Chemistry', 'Biology', 'Psychology', 'Education', 'Business', 'Law', 'Medicine'],
        'scraper_enabled': True,
        'supports_hebrew': True
    }
}

MOCK_COURSES = [
    {
        'id': 'cs101',
        'code': 'CS 101',
        'name': 'Introduction to Computer Science',
        'department': 'Computer Science',
        'credits': 3,
        'description': 'Fundamental concepts in computer science and programming.',
        'prerequisites': [],
        'sections': [
            {
                'id': 'cs101-001',
                'section': '001',
                'professor': 'Dr. Sarah Chen',
                'times': [
                    {'type': 'lecture', 'day': 'Mon', 'startTime': 9, 'endTime': 11},
                    {'type': 'lecture', 'day': 'Wed', 'startTime': 9, 'endTime': 11},
                    {'type': 'lab', 'day': 'Fri', 'startTime': 14, 'endTime': 16}
                ],
                'capacity': 120,
                'enrolled': 85,
                'location': 'Science Building 101',
                'status': 'open'
            }
        ]
    }
]

@university_router.get("/universities")
async def get_universities():
    return {
        'universities': list(UNIVERSITIES.values()),
        'total': len(UNIVERSITIES)
    }

@university_router.get("/universities/{university_id}")
async def get_university_details(university_id: str):
    if university_id not in UNIVERSITIES:
        raise HTTPException(status_code=404, detail="University not found")
    return UNIVERSITIES[university_id]

@university_router.get("/universities/{university_id}/courses")
async def get_university_courses(
    university_id: str, 
    semester: str = "fall", 
    year: str = "2024",
    department: str = "",
    search: str = "",
    user: Dict = Depends(get_current_user)
):
    if university_id not in UNIVERSITIES:
        raise HTTPException(status_code=404, detail="University not found")
        
    if UNIVERSITIES[university_id]['hasApi']:
        # Mocking API fetch
        return {
            'hasApi': True,
            'courses': MOCK_COURSES, # Simplified for brevity
            'semester': semester,
            'year': year,
            'university': UNIVERSITIES[university_id]
        }
    else:
        return {
            'hasApi': False,
            'message': 'This university requires manual course entry',
            'catalogUrl': UNIVERSITIES[university_id].get('catalogUrl'),
            'courses': []
        }

@university_router.get("/universities/{university_id}/departments")
async def get_university_departments(university_id: str):
    if university_id not in UNIVERSITIES:
        raise HTTPException(status_code=404, detail="University not found")
    return {
        'departments': UNIVERSITIES[university_id].get('departments', []),
        'university': UNIVERSITIES[university_id]['name']
    }

@university_router.post("/courses/convert")
async def convert_catalog_courses(data: Dict[str, Any], user: Dict = Depends(get_current_user)):
    if 'selectedCourses' not in data:
        raise HTTPException(status_code=400, detail="Missing course selections")
    if not isinstance(data['selectedCourses'], list):
        raise HTTPException(status_code=400, detail="selectedCourses must be an array")

    converted_courses: List[Dict[str, Any]] = []

    for selection in data['selectedCourses']:
        if not isinstance(selection, dict):
            continue

        course_info = selection.get('course') or {}
        section_info = selection.get('section') or {}

        name = (
            course_info.get('name')
            or course_info.get('courseName')
            or selection.get('name')
            or ""
        )
        code = course_info.get('code') or selection.get('code')
        if code and code not in name:
            name = f"{code} - {name}" if name else str(code)

        scheduler_course = {
            'name': name,
            'hasLecture': False,
            'hasPractice': False,
            'lectures': [],
            'practices': []
        }

        section_times = section_info.get('times')
        if not isinstance(section_times, list):
            section_times = []

        for time_slot in section_times:
            if not isinstance(time_slot, dict):
                continue

            day = time_slot.get('day')
            start_time = time_slot.get('startTime')
            end_time = time_slot.get('endTime')

            if not day or start_time is None or end_time is None:
                continue

            normalized_slot = {
                'day': str(day),
                'startTime': str(start_time),
                'endTime': str(end_time)
            }

            slot_type = str(time_slot.get('type', '')).lower()
            if slot_type == 'lecture':
                scheduler_course['hasLecture'] = True
                scheduler_course['lectures'].append(normalized_slot)
            elif slot_type in {'lab', 'practice', 'tutorial', 'ta'}:
                scheduler_course['hasPractice'] = True
                scheduler_course['practices'].append(normalized_slot)
            else:
                # Default unknown session types to lectures to avoid silent data loss.
                scheduler_course['hasLecture'] = True
                scheduler_course['lectures'].append(normalized_slot)

        if not scheduler_course['name']:
            continue

        converted_courses.append(scheduler_course)
    
    return {
        'courses': converted_courses,
        'message': f"Converted {len(converted_courses)} courses"
    }
