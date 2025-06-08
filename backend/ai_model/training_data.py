TRAIN_DATA = [
    # Time constraints - morning
    ("I don't want any classes before 10am", {
        "entities": [(32, 36, "NO_CLASS_BEFORE")]
    }),
    ("No classes before 9am", {
        "entities": [(18, 21, "NO_CLASS_BEFORE")]
    }),
    ("Please don't schedule anything before 8:30am", {
        "entities": [(38, 44, "NO_CLASS_BEFORE")]
    }),
    ("Can't do early morning classes before 11am", {
        "entities": [(38, 42, "NO_CLASS_BEFORE")]
    }),
    ("Prefer no classes earlier than 10:00", {
        "entities": [(31, 36, "NO_CLASS_BEFORE")]
    }),
    ("I need classes to start after 10:30am", {
        "entities": [(30, 37, "NO_CLASS_BEFORE")]
    }),
    ("Cannot attend anything before 9:15 in the morning", {
        "entities": [(30, 34, "NO_CLASS_BEFORE")]
    }),
    ("Please schedule after 11:00am only", {
        "entities": [(22, 29, "NO_CLASS_BEFORE")]
    }),
    ("I prefer classes that start after 10:45", {
        "entities": [(34, 39, "NO_CLASS_BEFORE")]
    }),
    ("Avoid scheduling classes before 9:00am", {
        "entities": [(32, 38, "NO_CLASS_BEFORE")]
    }),

    # Time constraints - variations
    ("I need all classes after 9", {
        "entities": [(25, 26, "NO_CLASS_BEFORE")]
    }),
    ("Nothing scheduled before noon please", {
        "entities": [(25, 29, "NO_CLASS_BEFORE")]
    }),
    ("Can't start before ten in the morning", {
        "entities": [(19, 22, "NO_CLASS_BEFORE")]
    }),
    ("Too early for 8:00 classes", {
        "entities": [(14, 18, "NO_CLASS_BEFORE")]
    }),
    

    # Day constraints
    ("No classes on Tuesday", {
        "entities": [(14, 21, "NO_CLASS_DAY")]
    }),
    ("I can't attend Wednesday classes", {
        "entities": [(15, 24, "NO_CLASS_DAY")]
    }),
    ("Please avoid scheduling on Monday", {
        "entities": [(27, 33, "NO_CLASS_DAY")]
    }),
    ("Thursday doesn't work for me", {
        "entities": [(0, 8, "NO_CLASS_DAY")]
    }),
    ("Can't do Friday classes", {
        "entities": [(9, 15, "NO_CLASS_DAY")]
    }),
    ("No Monday or Wednesday please", {
        "entities": [(3, 9, "NO_CLASS_DAY"), (13, 22, "NO_CLASS_DAY")]
    }),
    ("I have commitments every Tuesday", {
        "entities": [(25, 32, "NO_CLASS_DAY")]
    }),
    ("Wednesday is not possible for me", {
        "entities": [(0, 9, "NO_CLASS_DAY")]
    }),
    ("I'm unavailable on Thursdays", {
        "entities": [(19, 28, "NO_CLASS_DAY")]
    }),
    ("Monday and Friday don't work", {
        "entities": [(0, 6, "NO_CLASS_DAY"), (11, 17, "NO_CLASS_DAY")]
    }),
    ("Can't make it to class on Wednesday", {
        "entities": [(26, 35, "NO_CLASS_DAY")]
    }),
    

    # TA constraints
    ("I don't want TA Alex", {
        "entities": [(16, 20, "AVOID_TA")]
    }),
    ("Please not TA Sarah", {
        "entities": [(14, 19, "AVOID_TA")]
    }),
    ("Don't assign me to TA Mike", {
        "entities": [(22, 26, "AVOID_TA")]
    }),
    ("I had issues with TA Jordan last semester", {
        "entities": [(21, 27, "AVOID_TA")]
    }),

    # Combined constraints
    ("No early classes before 9am and no Tuesday classes", {
        "entities": [(24, 27, "NO_CLASS_BEFORE"), (35, 42, "NO_CLASS_DAY")]
    }),
    ("Can't do 8am or Wednesday classes", {
        "entities": [(9, 12, "NO_CLASS_BEFORE"), (16, 25, "NO_CLASS_DAY")]
    }),
    ("Avoid 7:30am and Friday sessions", {
        "entities": [(6, 12, "NO_CLASS_BEFORE"), (17, 23, "NO_CLASS_DAY")]
    }),
    ("No Monday morning classes before 10", {
        "entities": [(33, 35, "NO_CLASS_BEFORE")]
    }),

    # Additional variations of common patterns
    ("Classes shouldn't start until 10:45", {
        "entities": [(30, 35, "NO_CLASS_BEFORE")]
    }),
    ("Tuesday and Thursday mornings are impossible", {
        "entities": [(0, 7, "NO_CLASS_DAY"), (12, 20, "NO_CLASS_DAY")]
    }),
    ("TA Rodriguez has a conflict with my schedule", {
        "entities": [(3, 12, "AVOID_TA")]
    }),
    ("Cannot do anything earlier than 9:45am", {
        "entities": [(32, 38, "NO_CLASS_BEFORE")]
    })
]