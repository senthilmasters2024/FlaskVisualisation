import json

# Your JSON data
data = [
  {
    "Phrase1": "ChristianoRonaldo.txt",
    "Phrase2": "Aspirin.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.07459803312148565
  },
  {
    "Phrase1": "ChristianoRonaldo.txt",
    "Phrase2": "iboprofen.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.09903397662116371
  },
  {
    "Phrase1": "ChristianoRonaldo.txt",
    "Phrase2": "JobRequirement.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.12538476261131676
  },
  {
    "Phrase1": "ChristianoRonaldo.txt",
    "Phrase2": "paracetomol.txt.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.05216173653132632
  },
  {
    "Phrase1": "ChristianoRonaldo.txt",
    "Phrase2": "SachinTendulkarNewsArticle.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.393528248018886
  },
  {
    "Phrase1": "JobProfileCDeveloper.txt",
    "Phrase2": "Aspirin.txt",
    "domain": "jobvacancy",
    "SimilarityScore": -0.016096263623203412
  },
  {
    "Phrase1": "JobProfileCDeveloper.txt",
    "Phrase2": "iboprofen.txt",
    "domain": "jobvacancy",
    "SimilarityScore": 0.006234526462268183
  },
  {
    "Phrase1": "JobProfileCDeveloper.txt",
    "Phrase2": "JobRequirement.txt",
    "domain": "jobvacancy",
    "SimilarityScore": 0.6863929709725499
  },
  {
    "Phrase1": "JobProfileCDeveloper.txt",
    "Phrase2": "paracetomol.txt.txt",
    "domain": "jobvacancy",
    "SimilarityScore": 0.0034207695091580774
  },
  {
    "Phrase1": "JobProfileCDeveloper.txt",
    "Phrase2": "SachinTendulkarNewsArticle.txt",
    "domain": "jobvacancy",
    "SimilarityScore": 0.13486307131328207
  },
  {
    "Phrase1": "MedicalHistory.txt",
    "Phrase2": "Aspirin.txt",
    "domain": "Medical-MedicationSuggestion",
    "SimilarityScore": 0.33195745429772733
  },
  {
    "Phrase1": "MedicalHistory.txt",
    "Phrase2": "iboprofen.txt",
    "domain": "Medical-MedicationSuggestion",
    "SimilarityScore": 0.23717794093567096
  },
  {
    "Phrase1": "MedicalHistory.txt",
    "Phrase2": "JobRequirement.txt",
    "domain": "Medical-MedicationSuggestion",
    "SimilarityScore": 0.15897824254820653
  },
  {
    "Phrase1": "MedicalHistory.txt",
    "Phrase2": "paracetomol.txt.txt",
    "domain": "Medical-MedicationSuggestion",
    "SimilarityScore": 0.23864067770371952
  },
  {
    "Phrase1": "MedicalHistory.txt",
    "Phrase2": "SachinTendulkarNewsArticle.txt",
    "domain": "Medical-MedicationSuggestion",
    "SimilarityScore": 0.16838020131545448
  },
  {
    "Phrase1": "MSDhoni.txt",
    "Phrase2": "Aspirin.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.026687593772055433
  },
  {
    "Phrase1": "MSDhoni.txt",
    "Phrase2": "iboprofen.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.010836918179269881
  },
  {
    "Phrase1": "MSDhoni.txt",
    "Phrase2": "JobRequirement.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.11549445010066965
  },
  {
    "Phrase1": "MSDhoni.txt",
    "Phrase2": "paracetomol.txt.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.02196351114889793
  },
  {
    "Phrase1": "MSDhoni.txt",
    "Phrase2": "SachinTendulkarNewsArticle.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.5415616921075621
  },
  {
    "Phrase1": "SachinTendulkar.txt",
    "Phrase2": "Aspirin.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.07521079460166216
  },
  {
    "Phrase1": "SachinTendulkar.txt",
    "Phrase2": "iboprofen.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.05243897282142897
  },
  {
    "Phrase1": "SachinTendulkar.txt",
    "Phrase2": "JobRequirement.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.10582298657778909
  },
  {
    "Phrase1": "SachinTendulkar.txt",
    "Phrase2": "paracetomol.txt.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.08709043452917352
  },
  {
    "Phrase1": "SachinTendulkar.txt",
    "Phrase2": "SachinTendulkarNewsArticle.txt",
    "domain": "Unknown",
    "SimilarityScore": 0.7395233999998398
  }
]

# Function to remove .txt extension
def remove_txt_extension(filename):
    return filename.replace(".txt", "")

# Convert the data into the desired format
formatted_data = [
    (
        remove_txt_extension(item["Phrase1"]),
        remove_txt_extension(item["Phrase2"]),
        item["domain"],
        item["SimilarityScore"]
    )
    for item in data
]

# Print the formatted data
for item in formatted_data:
    print(item)