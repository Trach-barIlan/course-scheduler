TEST_DATA = [
("I can't attend any classes before 9:30am", {
    "entities": [(34, 40, "NO_CLASS_BEFORE")]
}),
("Please don't schedule anything on Thursday or Friday", {
    "entities": [(34, 42, "NO_CLASS_DAY"), (46, 52, "NO_CLASS_DAY")]
}),
("I prefer not to have TA Smith for this class", {
    "entities": [(24, 29, "AVOID_TA")]
}),
("No early morning classes before 8:15 and not on Monday", {
    "entities": [(32, 36, "NO_CLASS_BEFORE"), (48, 54, "NO_CLASS_DAY")]
}),
("Can't do classes at 7:45am or with TA Johnson", {
    "entities": [(20, 26, "NO_CLASS_BEFORE"), (38, 45, "AVOID_TA")]
}),
("Tuesday and Thursday are bad days for me", {
    "entities": [(0, 7, "NO_CLASS_DAY"), (12, 20, "NO_CLASS_DAY")]
}),
("Don't schedule anything with TA Brown nor before 10:30", {
    "entities": [(32, 37, "AVOID_TA"), (49, 54, "NO_CLASS_BEFORE")]
}),
("Would prefer no classes before eleven in the morning", {
    "entities": [(31, 37, "NO_CLASS_BEFORE")]
}),
("wednesday doesn't work, and I can't do 8am classes", {
    "entities": [(0, 9, "NO_CLASS_DAY"), (39, 42, "NO_CLASS_BEFORE")]
}),
("Please avoid TA Williams and early morning sessions", {
    "entities": [(16, 24, "AVOID_TA")]
}),
("I have a conflict with after 9:15pm classes", {
    "entities": [(29, 35, "NO_CLASS_AFTER")]
}),
("Avoid scheduling after 6pm", {
    "entities": [(23, 26, "NO_CLASS_AFTER")]
}),
("No classes after 15:00", {
    "entities": [(17, 22, "NO_CLASS_AFTER")]
}),
("I can't attend any sessions after noon", {
    "entities": [(34, 38, "NO_CLASS_AFTER")]
}),

]