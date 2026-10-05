from src.statement_analysis.extractor import (
    extract_time,
    extract_location,
)


statement = "The person left home at 6:30 PM."

extracted_time = extract_time(statement)
extracted_location = extract_location(statement)

print("Extracted time:")
print(extracted_time)

print("\nExtracted location:")
print(extracted_location)

assert extracted_time.hour == 18
assert extracted_time.minute == 30
assert extracted_location == "home"

print("\nPASS: Time and location extraction works.")