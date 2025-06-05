TRAIN_DATA = [
    ("I don't want any classes before 10am", {
        "entities": [(29, 34, "NO_CLASS_BEFORE")]
    }),
    ("No classes on Tuesday or Thursday", {
        "entities": [(14, 21, "NO_CLASS_DAY"), (25, 33, "NO_CLASS_DAY")]
    }),
    ("Don't schedule anything before 9am", {
        "entities": [(28, 32, "NO_CLASS_BEFORE")]
    }),
    ("I want no classes on Monday", {
        "entities": [(22, 28, "NO_CLASS_DAY")]
    }),
    ("Avoid morning classes before 11", {
        "entities": [(27, 29, "NO_CLASS_BEFORE")]
    }),
    ("Nothing on Thursday please", {
        "entities": [(9, 17, "NO_CLASS_DAY")]
    }),
    ("I don't want any classes before 10am", {
        "entities": [(29, 34, "NO_CLASS_BEFORE")]
    }),
    ("No classes on Tuesday or Thursday", {
        "entities": [(14, 21, "NO_CLASS_DAY"), (25, 33, "NO_CLASS_DAY")]
    }),

    # New examples for TAs and lecturers
    ("I don't want TA Alex", {
        "entities": [(13, 20, "AVOID_TA")]
    }),
    ("Avoid TA Dana", {
        "entities": [(6, 13, "AVOID_TA")]
    }),
    ("Please remove Professor Green from my schedule", {
        "entities": [(14, 30, "AVOID_LECTURER")]
    }),
    ("Don't give me any class with Prof. Chen", {
        "entities": [(31, 42, "AVOID_LECTURER")]
    }),
    ("I prefer Dr. Park", {
        "entities": [(9, 18, "PREFERS_LECTURER")]
    }),
    ("I'd like to have more classes with Dr. Wu", {
        "entities": [(35, 42, "PREFERS_LECTURER")]
    })
]
