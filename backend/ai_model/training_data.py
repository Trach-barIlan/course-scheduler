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
]
    