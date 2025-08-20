from flask import Blueprint, request, jsonify
from auth.routes import token_required

university_bp = Blueprint('university', __name__)

# Mock university data - replace with real integrations
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
    # Israeli Universities
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

# Mock course data
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
            },
            {
                'id': 'cs101-002',
                'section': '002',
                'professor': 'Prof. Michael Rodriguez',
                'times': [
                    {'type': 'lecture', 'day': 'Tue', 'startTime': 13, 'endTime': 15},
                    {'type': 'lecture', 'day': 'Thu', 'startTime': 13, 'endTime': 15},
                    {'type': 'lab', 'day': 'Fri', 'startTime': 16, 'endTime': 18}
                ],
                'capacity': 120,
                'enrolled': 92,
                'location': 'Science Building 102',
                'status': 'open'
            }
        ]
    },
    {
        'id': 'math201',
        'code': 'MATH 201', 
        'name': 'Calculus I',
        'department': 'Mathematics',
        'credits': 4,
        'description': 'Limits, derivatives, and applications of differential calculus.',
        'prerequisites': ['MATH 101'],
        'sections': [
            {
                'id': 'math201-001',
                'section': '001',
                'professor': 'Dr. Emily Watson',
                'times': [
                    {'type': 'lecture', 'day': 'Mon', 'startTime': 10, 'endTime': 12},
                    {'type': 'lecture', 'day': 'Wed', 'startTime': 10, 'endTime': 12}, 
                    {'type': 'lecture', 'day': 'Fri', 'startTime': 10, 'endTime': 11}
                ],
                'capacity': 200,
                'enrolled': 178,
                'location': 'Math Building 201',
                'status': 'open'
            }
        ]
    },
    {
        'id': 'eng102',
        'code': 'ENG 102',
        'name': 'Academic Writing', 
        'department': 'English',
        'credits': 3,
        'description': 'Advanced writing skills for academic and professional contexts.',
        'prerequisites': ['ENG 101'],
        'sections': [
            {
                'id': 'eng102-001',
                'section': '001',
                'professor': 'Prof. David Kim',
                'times': [
                    {'type': 'lecture', 'day': 'Tue', 'startTime': 11, 'endTime': 12},
                    {'type': 'lecture', 'day': 'Thu', 'startTime': 11, 'endTime': 12}
                ],
                'capacity': 25,
                'enrolled': 23,
                'location': 'Humanities 150',
                'status': 'open'
            },
            {
                'id': 'eng102-002', 
                'section': '002',
                'professor': 'Dr. Lisa Park',
                'times': [
                    {'type': 'lecture', 'day': 'Mon', 'startTime': 14, 'endTime': 15},
                    {'type': 'lecture', 'day': 'Wed', 'startTime': 14, 'endTime': 15}
                ],
                'capacity': 25,
                'enrolled': 20,
                'location': 'Humanities 152',
                'status': 'open'
            }
        ]
    }
]

@university_bp.route('/universities', methods=['GET'])
def get_universities():
    """Get list of supported universities"""
    try:
        return jsonify({
            'universities': list(UNIVERSITIES.values()),
            'total': len(UNIVERSITIES)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@university_bp.route('/universities/<university_id>', methods=['GET'])
def get_university_details(university_id):
    """Get details for a specific university"""
    try:
        if university_id not in UNIVERSITIES:
            return jsonify({'error': 'University not found'}), 404
            
        return jsonify(UNIVERSITIES[university_id]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@university_bp.route('/universities/<university_id>/courses', methods=['GET'])
@token_required
def get_university_courses(university_id):
    """Get courses for a specific university and semester"""
    try:
        if university_id not in UNIVERSITIES:
            return jsonify({'error': 'University not found'}), 404
            
        # Get query parameters
        semester = request.args.get('semester', 'fall')
        year = request.args.get('year', '2024')
        department = request.args.get('department', '')
        search = request.args.get('search', '')
        
        # In a real implementation, this would call the university's API
        # or scrape their course catalog based on the university's configuration
        
        if UNIVERSITIES[university_id]['hasApi']:
            # Simulate API call
            courses = fetch_courses_from_api(university_id, semester, year, department, search)
        else:
            # For universities without API, return instructions for manual import
            return jsonify({
                'hasApi': False,
                'message': 'This university requires manual course entry',
                'catalogUrl': UNIVERSITIES[university_id].get('catalogUrl'),
                'courses': []
            }), 200
            
        return jsonify({
            'hasApi': True,
            'courses': courses,
            'semester': semester,
            'year': year,
            'university': UNIVERSITIES[university_id]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@university_bp.route('/universities/<university_id>/departments', methods=['GET'])
def get_university_departments(university_id):
    """Get departments for a specific university"""
    try:
        if university_id not in UNIVERSITIES:
            return jsonify({'error': 'University not found'}), 404
            
        university = UNIVERSITIES[university_id]
        departments = university.get('departments', [])
        
        return jsonify({
            'departments': departments,
            'university': university['name']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@university_bp.route('/courses/convert', methods=['POST'])
@token_required  
def convert_catalog_courses():
    """Convert selected catalog courses to scheduler format"""
    try:
        data = request.json
        if not data or 'selectedCourses' not in data:
            return jsonify({'error': 'Missing course selections'}), 400
            
        selected_courses = data['selectedCourses']
        converted_courses = []
        
        for selection in selected_courses:
            course = selection['course']
            section = selection['section']
            
            # Convert to scheduler format
            scheduler_course = {
                'name': f"{course['code']} - {course['name']}",
                'hasLecture': False,
                'hasPractice': False,
                'lectures': [],
                'practices': []
            }
            
            # Process section times
            for time_slot in section['times']:
                slot_data = {
                    'day': time_slot['day'],
                    'startTime': time_slot['startTime'],
                    'endTime': time_slot['endTime']
                }
                
                if time_slot['type'] == 'lecture':
                    scheduler_course['lectures'].append(slot_data)
                    scheduler_course['hasLecture'] = True
                else:  # lab, tutorial, etc.
                    scheduler_course['practices'].append(slot_data)
                    scheduler_course['hasPractice'] = True
                    
            converted_courses.append(scheduler_course)
            
        return jsonify({
            'courses': converted_courses,
            'message': f'Successfully converted {len(converted_courses)} courses'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def fetch_courses_from_api(university_id, semester, year, department, search):
    """
    Mock function to simulate fetching courses from university APIs
    In a real implementation, this would make actual API calls or web scraping
    """
    
    # Filter mock courses based on parameters
    filtered_courses = MOCK_COURSES.copy()
    
    if department:
        filtered_courses = [c for c in filtered_courses if c['department'] == department]
        
    if search:
        search_lower = search.lower()
        filtered_courses = [
            c for c in filtered_courses 
            if search_lower in c['name'].lower() or 
               search_lower in c['code'].lower() or
               any(search_lower in section['professor'].lower() 
                   for section in c['sections'])
        ]
    
    return filtered_courses

# University-specific integration functions
class UniversityIntegrator:
    """Base class for university integrations"""
    
    def __init__(self, university_config):
        self.config = university_config
        
    def fetch_courses(self, semester, year, **filters):
        raise NotImplementedError
        
    def fetch_course_details(self, course_id):
        raise NotImplementedError

class HarvardIntegrator(UniversityIntegrator):
    """Harvard University course catalog integration"""
    
    def fetch_courses(self, semester, year, **filters):
        # Implementation would use Harvard's actual API
        # For now, return mock data
        return MOCK_COURSES
        
class MITIntegrator(UniversityIntegrator):
    """MIT course catalog integration"""
    
    def fetch_courses(self, semester, year, **filters):
        # Implementation would use MIT's actual API
        # For now, return mock data
        return MOCK_COURSES
