# Frontend Implementation Guide: Real-time Constraint Pills

This guide explains how to implement the real-time constraint feedback feature on the Schedgic frontend using the new GLiNER-based backend endpoint.

## 1. The Goal
As the user types in the "Schedule Constraints" text box, the application should instantly show "Pills" (tags) below the input field that reflect what the AI has understood.

**Example:**
*   **User Types:** "No classes before 10am or on Monday"
*   **UI Shows:** `[Starts after 10:00] (Blue)` `[No Mon] (Red)`

---

## 2. API Integration
The backend now provides a dedicated lightweight endpoint for live parsing.

*   **Endpoint:** `POST /api/parse-live`
*   **Request Body:**
    ```json
    { "text": "I can't do classes before 10am" }
    ```
*   **Response Body:**
    ```json
    [
      {
        "label": "Starts after 10:00",
        "color": "blue",
        "type": "no_classes_before"
      }
    ]
    ```

---

## 3. Frontend Logic (React/Vue/JS)

### Step A: The Debounce
To avoid hitting the server on every single keystroke, implement a **debounce** of 300ms-500ms.

```javascript
// Using lodash or a custom hook
const handleTextChange = debounce((text) => {
  if (text.length < 3) {
    setLiveConstraints([]);
    return;
  }
  fetchLiveConstraints(text);
}, 300);
```

### Step B: Fetching Data
Call the `/api/parse-live` endpoint. **Note:** This endpoint is optimized for speed and does not require a Token (unless you choose to add `@token_required` back in `app.py`).

```javascript
async function fetchLiveConstraints(text) {
  try {
    const response = await fetch('/api/parse-live', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ text })
    });
    const data = await response.json();
    setLiveConstraints(Array.isArray(data) ? data : []);
  } catch (error) {
    console.error("Live parsing failed", error);
  }
}
```

### Step C: UI Component (The Pills)
Render the constraints list as small badges below the text area.

```jsx
<div className="flex flex-wrap gap-2 mt-2">
  {liveConstraints.map((pill, index) => (
    <span 
      key={index}
      className={`px-2 py-1 rounded-full text-sm font-medium bg-${pill.color}-100 text-${pill.color}-800 border border-${pill.color}-200`}
    >
      {pill.label}
    </span>
  ))}
</div>
```

---

## 4. Why this is better
1.  **Transparency:** Users see if the AI misinterprets "after 4pm" as "before 4pm" immediately.
2.  **No Deadlines:** Users don't have to wait for the "Generate" button to see if their constraints were valid.
3.  **Visual Appeal:** It makes the application feel "smart" and modern, similar to tools like Notion or Gmail.

---

## 5. Security Note
The live endpoint is intentionally lightweight. It does not perform heavy database logging or complex verification, making it safe for high-frequency use as a student types.
