import React, { useState, useEffect } from 'react';
import '../styles/UniversitySelector.css';

const UniversitySelector = ({ user, authToken, onUniversitySelected }) => {
  const [selectedUniversity, setSelectedUniversity] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [universities, setUniversities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [importMethod, setImportMethod] = useState('manual'); // 'catalog' or 'manual' - default to manual since no APIs
  const [semester, setSemester] = useState(() => {
    const month = new Date().getMonth();
    const currentSemester = month >= 8 || month <= 0 ? 'fall' : (month >= 1 && month <= 5 ? 'spring' : 'summer');
    console.log('Initializing semester:', currentSemester, 'for month:', month);
    return currentSemester;
  });
  const [year, setYear] = useState(new Date().getFullYear());
  
  const API_BASE_URL = process.env.REACT_APP_API_BASE_URL;

  // Mock university data - replace with real API
  const mockUniversities = [
    // United States Universities
    {
      id: 'harvard',
      name: 'Harvard University',
      location: 'Cambridge, MA',
      country: 'USA',
      hasApi: true,
      catalogUrl: 'https://courses.harvard.edu',
      logo: 'https://1000logos.net/wp-content/uploads/2017/02/Harvard-Logo.png'
    },
    {
      id: 'mit',
      name: 'Massachusetts Institute of Technology',
      location: 'Cambridge, MA', 
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://student.mit.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/MIT_logo.svg/256px-MIT_logo.svg.png'
    },
    {
      id: 'stanford',
      name: 'Stanford University',
      location: 'Stanford, CA',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://explorecourses.stanford.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Seal_of_Leland_Stanford_Junior_University.svg/256px-Seal_of_Leland_Stanford_Junior_University.svg.png'
    },
    {
      id: 'yale',
      name: 'Yale University',
      location: 'New Haven, CT',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://courses.yale.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/07/Yale_University_Shield_1.svg/256px-Yale_University_Shield_1.svg.png'
    },
    {
      id: 'princeton',
      name: 'Princeton University',
      location: 'Princeton, NJ',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://registrar.princeton.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Princeton_shield.svg/256px-Princeton_shield.svg.png'
    },
    {
      id: 'columbia',
      name: 'Columbia University',
      location: 'New York, NY',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://bulletins.columbia.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Columbia_University_logo.svg/256px-Columbia_University_logo.svg.png'
    },
    {
      id: 'berkeley',
      name: 'UC Berkeley',
      location: 'Berkeley, CA',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://classes.berkeley.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Seal_of_University_of_California%2C_Berkeley.svg/256px-Seal_of_University_of_California%2C_Berkeley.svg.png'
    },
    {
      id: 'ucla',
      name: 'UCLA',
      location: 'Los Angeles, CA',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://sa.ucla.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0d/The_University_of_California_UCLA.svg/256px-The_University_of_California_UCLA.svg.png'
    },
    {
      id: 'nyu',
      name: 'New York University',
      location: 'New York, NY',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://albert.nyu.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/New_York_University_logo.svg/256px-New_York_University_logo.svg.png'
    },
    {
      id: 'chicago',
      name: 'University of Chicago',
      location: 'Chicago, IL',
      country: 'USA',
      hasApi: false,
      catalogUrl: 'https://classes.uchicago.edu',
      logo: 'https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/University_of_Chicago_shield.svg/256px-University_of_Chicago_shield.svg.png'
    },
    // Israeli Universities
    {
      id: 'hebrew-university',
      name: 'Hebrew University of Jerusalem',
      location: 'Jerusalem',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://shnaton.huji.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6d/Hebrew_University_Logo.svg/256px-Hebrew_University_Logo.svg.png'
    },
    {
      id: 'technion',
      name: 'Technion - Israel Institute of Technology',
      location: 'Haifa',
      country: 'Israel', 
      hasApi: false,
      catalogUrl: 'https://ug.technion.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/8/81/Technion_Israel_Institute_of_Technology_logo.svg/256px-Technion_Israel_Institute_of_Technology_logo.svg.png'
    },
    {
      id: 'tel-aviv',
      name: 'Tel Aviv University',
      location: 'Tel Aviv',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.tau.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/c/c2/Tel_Aviv_University_Logo.svg/256px-Tel_Aviv_University_Logo.svg.png'
    },
    {
      id: 'weizmann',
      name: 'Weizmann Institute of Science',
      location: 'Rehovot',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.weizmann.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/5/5e/Weizmann_Institute_of_Science_logo.svg/256px-Weizmann_Institute_of_Science_logo.svg.png'
    },
    {
      id: 'bar-ilan',
      name: 'Bar-Ilan University',
      location: 'Ramat Gan',
      country: 'Israel',
      hasApi: true,
      catalogUrl: 'https://courses.biu.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/c/cd/Bar-Ilan_University_logo.svg/256px-Bar-Ilan_University_logo.svg.png'
    },
    {
      id: 'ben-gurion',
      name: 'Ben-Gurion University of the Negev',
      location: 'Beer Sheva',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.bgu.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/f/f5/Ben-Gurion_University_of_the_Negev_logo.svg/256px-Ben-Gurion_University_of_the_Negev_logo.svg.png'
    },
    {
      id: 'haifa',
      name: 'University of Haifa',
      location: 'Haifa',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.haifa.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/0/0c/University_of_Haifa_logo.svg/256px-University_of_Haifa_logo.svg.png'
    },
    {
      id: 'idc-herzliya',
      name: 'Reichman University (IDC Herzliya)',
      location: 'Herzliya',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.runi.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/8/8c/Reichman_University_logo.svg/256px-Reichman_University_logo.svg.png'
    },
    {
      id: 'open-university',
      name: 'Open University of Israel',
      location: 'Ra\'anana',
      country: 'Israel',
      hasApi: false,
      catalogUrl: 'https://www.openu.ac.il',
      logo: 'https://upload.wikimedia.org/wikipedia/en/thumb/3/3f/Open_University_of_Israel_logo.svg/256px-Open_University_of_Israel_logo.svg.png'
    }
  ];

  useEffect(() => {
    const fetchUniversities = async () => {
      setIsLoading(true);
      try {
        console.log('Fetching universities from API...');
        const response = await fetch(`${API_BASE_URL}/api/university/universities`);
        
        if (response.ok) {
          const data = await response.json();
          console.log('API response received:', data);
          const allUniversities = data.universities || mockUniversities;
          console.log('Using API data, Bar-Ilan hasApi:', allUniversities.find(u => u.id === 'bar-ilan')?.hasApi);
          
          // Filter universities based on search query and country
          const filtered = allUniversities.filter(uni => {
            const matchesSearch = uni.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                uni.location.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCountry = !selectedCountry || uni.country === selectedCountry;
            return matchesSearch && matchesCountry;
          });
          setUniversities(filtered);
        } else {
          console.error('Failed to fetch universities, using mock data');
          console.log('Using mock data, Bar-Ilan hasApi:', mockUniversities.find(u => u.id === 'bar-ilan')?.hasApi);
          // Filter mock universities based on search query and country
          const filtered = mockUniversities.filter(uni => {
            const matchesSearch = uni.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                                uni.location.toLowerCase().includes(searchQuery.toLowerCase());
            const matchesCountry = !selectedCountry || uni.country === selectedCountry;
            return matchesSearch && matchesCountry;
          });
          setUniversities(filtered);
        }
      } catch (error) {
        console.error('Error fetching universities:', error);
        console.log('Using mock data due to error, Bar-Ilan hasApi:', mockUniversities.find(u => u.id === 'bar-ilan')?.hasApi);
        // Filter mock universities based on search query and country
        const filtered = mockUniversities.filter(uni => {
          const matchesSearch = uni.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                              uni.location.toLowerCase().includes(searchQuery.toLowerCase());
          const matchesCountry = !selectedCountry || uni.country === selectedCountry;
          return matchesSearch && matchesCountry;
        });
        setUniversities(filtered);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUniversities();
  }, [searchQuery, selectedCountry, API_BASE_URL]);

  const handleUniversitySelect = (university) => {
    console.log('University selected:', university);
    setSelectedUniversity(university);
    // Auto-set import method based on university capabilities
    const newImportMethod = university.hasApi ? 'catalog' : 'manual';
    console.log('Setting import method to:', newImportMethod, 'for', university.name);
    setImportMethod(newImportMethod);
  };

  const handleContinue = () => {
    if (selectedUniversity && onUniversitySelected) {
      const config = {
        university: selectedUniversity,
        importMethod,
        semester: semester || 'fall', // Default to fall if empty
        year
      };
      console.log('Continuing with config:', config);
      onUniversitySelected(config);
    }
  };

  const getCurrentSemester = () => {
    const month = new Date().getMonth();
    if (month >= 8 || month <= 0) return 'fall';
    if (month >= 1 && month <= 5) return 'spring';
    return 'summer';
  };

  return (
    <div className="university-selector-container">
      <div className="university-selector-header">
        <h1>Select Your University</h1>
        <p>Choose your institution to import courses and create your schedule</p>
      </div>

      <div className="search-section">
        <div className="search-controls">
          <div className="search-bar">
            <input
              type="text"
              placeholder="Search universities by name or location..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="university-search-input"
            />
          </div>
          <div className="country-filter">
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="country-select"
            >
              <option value="">All Countries</option>
              <option value="USA">🇺🇸 United States</option>
              <option value="Israel">🇮🇱 Israel</option>
            </select>
          </div>
        </div>
      </div>

      {!isLoading && (
        <div className="universities-stats">
          Found {universities.length} universit{universities.length !== 1 ? 'ies' : 'y'}
          {selectedCountry && ` in ${selectedCountry === 'USA' ? 'United States' : selectedCountry}`}
        </div>
      )}

      {isLoading ? (
        <div className="loading-state">
          <div className="loading-spinner"></div>
          <p>Loading universities...</p>
        </div>
      ) : (
        <div className="universities-grid">
          {universities.map((university) => (
            <div
              key={university.id}
              className={`university-card ${selectedUniversity?.id === university.id ? 'selected' : ''}`}
              onClick={() => handleUniversitySelect(university)}
            >            <div className="university-logo">
              {university.logo ? (
                <img 
                  src={university.logo} 
                  alt={`${university.name} logo`}
                  className="logo-image"
                  onError={(e) => {
                    e.target.style.display = 'none';
                    e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div className="logo-placeholder" style={{ display: university.logo ? 'none' : 'flex' }}>
                {university.name.charAt(0)}
              </div>
            </div>            <div className="university-info">
              <h3 className="university-name">{university.name}</h3>
              <p className="university-location">
                <span className="country-flag">
                  {university.country === 'USA' ? '🇺🇸' : university.country === 'Israel' ? '🇮🇱' : '🌍'}
                </span>
                {university.location}, {university.country}
              </p>
              <div className="university-features">
                {university.hasApi ? (
                  <span className="feature-badge api-available">📡 Auto Import</span>
                ) : (
                  <span className="feature-badge manual-import">📝 Manual Import</span>
                )}
              </div>
            </div>
            </div>
          ))}
        </div>
      )}

      {universities.length === 0 && searchQuery && (
        <div className="no-results">
          <div className="no-results-icon">🏫</div>
          <h3>University not found?</h3>
          <p>We're constantly adding new universities. In the meantime, you can:</p>
          <ul>
            <li>Use the manual course entry option</li>
            <li>Request your university to be added</li>
            <li>Import your schedule from a file</li>
          </ul>
          <button className="add-university-btn">
            Request University Addition
          </button>
        </div>
      )}

      {selectedUniversity && (
        <div className="university-details">
          <div className="details-header">
            <h3>Import Options for {selectedUniversity.name}</h3>
          </div>
          
          <div className="import-methods">
            <div className={`import-method ${importMethod === 'catalog' ? 'selected' : ''}`}>
              <label>
                <input
                  type="radio"
                  name="importMethod"
                  value="catalog"
                  checked={importMethod === 'catalog'}
                  onChange={(e) => setImportMethod(e.target.value)}
                  disabled={!selectedUniversity.hasApi}
                />
                <div className="method-content">
                  <div className="method-icon">📚</div>
                  <div className="method-info">
                    <h4>Course Catalog Import</h4>
                    <p>Automatically fetch courses, times, and professors</p>
                    {!selectedUniversity.hasApi && (
                      <span className="not-available">Not available for this university</span>
                    )}
                  </div>
                </div>
              </label>
            </div>

            <div className={`import-method ${importMethod === 'manual' ? 'selected' : ''}`}>
              <label>
                <input
                  type="radio"
                  name="importMethod"
                  value="manual"
                  checked={importMethod === 'manual'}
                  onChange={(e) => setImportMethod(e.target.value)}
                />
                <div className="method-content">
                  <div className="method-icon">✏️</div>
                  <div className="method-info">
                    <h4>Manual Entry</h4>
                    <p>Enter course information manually</p>
                  </div>
                </div>
              </label>
            </div>
          </div>

          {importMethod === 'catalog' && selectedUniversity.hasApi && (
            <div className="semester-selection">
              <h4>Select Semester</h4>
              <div className="semester-inputs">
                <select
                  value={semester || getCurrentSemester()}
                  onChange={(e) => setSemester(e.target.value)}
                  className="semester-select"
                >
                  <option value="fall">Fall</option>
                  <option value="spring">Spring</option>
                  <option value="summer">Summer</option>
                </select>
                <input
                  type="number"
                  value={year}
                  onChange={(e) => setYear(parseInt(e.target.value))}
                  min="2020"
                  max="2030"
                  className="year-input"
                />
              </div>
            </div>
          )}

          <div className="continue-section">
            <button 
              className="continue-btn"
              onClick={handleContinue}
              disabled={!selectedUniversity}
            >
              Continue with {selectedUniversity.name}
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default UniversitySelector;
