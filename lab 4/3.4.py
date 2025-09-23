# Define a list of survey response values
survey_responses = [5, 7, 3, 8]
survey_responses.append(0)
survey_responses.insert(2,6)
# Define a tuple of respondent ID values
respondent_ids = (1012, 1035, 1021, 1053)

# Append the tuple to the list
survey_responses.append(respondent_ids)

# Print out the list
print(survey_responses)