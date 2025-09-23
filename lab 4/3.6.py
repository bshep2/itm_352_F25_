# Original tuple of respondent IDs
respondent_ids = (1012, 1035, 1021, 1053)

# Attempting to add a new respondent ID
new_id = 1011
new_respondent_ids = respondent_ids + (new_id,)

print(new_respondent_ids)