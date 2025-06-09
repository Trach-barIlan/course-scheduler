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

# Time constraints - afternoon/evening
("No classes after 3pm", {
    "entities": [(17, 20, "NO_CLASS_AFTER")]
}),
("Don't schedule anything after 4:30pm", {
    "entities": [(30, 36, "NO_CLASS_AFTER")]
}),
("I want to be done by 5pm", {
    "entities": [(21, 24, "NO_CLASS_AFTER")]
}),
("Nothing scheduled past 6:00", {
    "entities": [(23, 27, "NO_CLASS_AFTER")]
}),
("Classes must end before 7pm", {
    "entities": [(24, 27, "NO_CLASS_AFTER")]
}),
("Please avoid classes after 8:15", {
    "entities": [(27, 31, "NO_CLASS_AFTER")]
}),
("I prefer no classes after 5:30pm", {
    "entities": [(26, 32, "NO_CLASS_AFTER")]
}),
("Avoid scheduling anything after 6:45", {
    "entities": [(32, 36, "NO_CLASS_AFTER")]
}),
("I can't attend classes after 4", {
    "entities": [(29, 30, "NO_CLASS_AFTER")]
}),
("No late classes after 8pm", {
    "entities": [(22, 25, "NO_CLASS_AFTER")]
}),
("Please don't schedule anything after 7:00pm", {
    "entities": [(37, 43, "NO_CLASS_AFTER")]
}),
("Nothing after 5:15 in the evening", {
    "entities": [(14, 18, "NO_CLASS_AFTER")]
}),
("Classes should not be scheduled after 6pm", {
    "entities": [(38, 41, "NO_CLASS_AFTER")]
}),
("I prefer no classes after 9:30pm", {
    "entities": [(26, 32, "NO_CLASS_AFTER")]
}),
("Please avoid scheduling after 10pm", {
    "entities": [(30, 34, "NO_CLASS_AFTER")]
}),
("classes after 4 don't work for me", {
    "entities": [(14, 15, "NO_CLASS_AFTER")]
}),
("5pm classes are too late", {
    "entities": [(0, 3, "NO_CLASS_AFTER")]
}),
("Nothing after 3:30pm", {
    "entities": [(14, 20, "NO_CLASS_AFTER")]
}),
("Classes should not be scheduled after 2pm", {
    "entities": [(38, 41, "NO_CLASS_AFTER")]
}),
("Please avoid scheduling after 1pm", {
    "entities": [(30, 33, "NO_CLASS_AFTER")]
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
("I don't want to learn with Emily as my ta", {
    "entities": [(27, 32, "AVOID_TA")]
}),
("Avoid TA Chris for this course", {
    "entities": [(9, 14, "AVOID_TA")]
}),

("I prefer not to have TA Taylor", {
    "entities": [(24, 30, "AVOID_TA")]
}),
("Please avoid TA Jamie", {
    "entities": [(16, 21, "AVOID_TA")]
}),
("I can't work with TA Morgan", {
    "entities": [(21, 27, "AVOID_TA")]
}),
("I had a bad experience with TA Casey", {
    "entities": [(31, 36, "AVOID_TA")]
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
("No classes with TA Smith or after 5pm", {
    "entities": [(19, 24, "AVOID_TA"), (34, 37, "NO_CLASS_AFTER")]
}),
("Avoid any classes after 7 and no Thursday sessions", {
    "entities": [(24, 25, "NO_CLASS_AFTER"), (33, 41, "NO_CLASS_DAY")]
}),
("Nothing before 9am nor after 4pm", {
    "entities": [(15, 18, "NO_CLASS_BEFORE"), (29, 32, "NO_CLASS_AFTER")]
}),
("I can't do classes before 10:30am or with TA Johnson", {
    "entities": [(26, 33, "NO_CLASS_BEFORE"), (45, 52, "AVOID_TA")]
}),
("Please avoid scheduling before 8:15am and after 6pm", {
    "entities": [(31, 37, "NO_CLASS_BEFORE"), (48, 51, "NO_CLASS_AFTER")]
}),
("I prefer no classes on monday or with TA Brown", {
    "entities": [(23, 29, "NO_CLASS_DAY"), (41, 46, "AVOID_TA")]
}),
("Don't schedule anything after 6:00pm or after 5:30pm", {
    "entities": [(30, 36, "NO_CLASS_AFTER"), (46, 52, "NO_CLASS_AFTER")]
}),
("Classes should not be scheduled before 10am or after 3pm", {
    "entities": [(39, 43, "NO_CLASS_BEFORE"), (53, 56, "NO_CLASS_AFTER")]
}),

("Nothing should be after 19 or on Mondays", {
    "entities": [(24, 26, "NO_CLASS_AFTER"), (33, 40, "NO_CLASS_DAY")]
}),
("After 8pm classes are not suitable and I can't do Friday", {
    "entities": [(6, 9, "NO_CLASS_AFTER"), (50, 56, "NO_CLASS_DAY")]
}),
("8pm classes are too late and I can't do Thursdays", {
    "entities": [(0, 3, "NO_CLASS_AFTER"), (40, 49, "NO_CLASS_DAY")]
}),
("Avoid scheduling classes before 9:00am and after 5:00pm", {
    "entities": [(32, 38, "NO_CLASS_BEFORE"), (49, 55, "NO_CLASS_AFTER")]
}),
("I can't attend classes before 10:15am or after 6:30pm", {
    "entities": [(30, 37, "NO_CLASS_BEFORE"), (47, 53, "NO_CLASS_AFTER")]
}),
("No classes on Tuesday mornings or with TA Smith", {
    "entities": [(14, 21, "NO_CLASS_DAY"), (42, 47, "AVOID_TA")]
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