# Semantic Similarity & KNN Classifier – Cloud Experiment

This repository contains a cloud-ready pipeline that builds **text embeddings** from PDFs, trains a **KNN classifier**, and performs **semantic similarity** analysis over documents and phrases.

It’s centered on the class `MyExperiment.Experiment`, which coordinates:
- Loading training PDFs and producing embeddings *(OpenAI `text-embedding-3-large`)*
- KNN classification of PDFs under `./documentstoclassify/`
- Document-level & phrase-level similarity routines
- Logging classification results to **Azure Table Storage**
- Saving files into label-based category folders

---

## Table of Contents
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Folder Structure](#folder-structure)
- [Configuration](#configuration)
- [Inputs](#inputs)
- [Outputs](#outputs)
- [Running Locally](#running-locally)
- [Running with Docker](#running-with-docker)
- [Deploying to Azure Container Instances (ACI)](#deploying-to-azure-container-instances-aci)
- [Queue Message Schema](#queue-message-schema)
- [Troubleshooting](#troubleshooting)
- [Security Notes](#security-notes)

---

## Architecture

**Core components** (names from this repo):
- `Experiment` — main orchestrator exposing `RunAsync(string inputData, IExperimentRequest request)`
- `PdfReaderService` — extracts text from PDFs
- `OpenAIEmbeddingService` — generates embeddings via OpenAI
- `KNNClassifier` — predicts labels based on cosine similarity
- `AzureTableLogger` — writes results to Azure Table Storage
- `ClassifiedFileHandler` — moves classified files into `/<label>/` folders
- `SemanticSimilarityForDocumentsWithInputDataDynamic` — document-level similarity
- `SemanticSimilarityPhrasesWithInputDataSet` — phrase-level similarity
- `ProcessingHandler` — selects & runs similarity workflows

> **Note:** Large image‑only PDFs may require OCR before meaningful embeddings can be produced.

---

## Prerequisites

- **.NET SDK 8.0+**
- **OpenAI API key** with access to embeddings (e.g., `text-embedding-3-large`)
- **Azure Storage** (Table & optionally Blob) if you use `AzureTableLogger`/blob ingestion
- (Optional) **Docker** if containerizing
- (Optional) **Azure Container Instances (ACI)** for cloud execution

Install the .NET tools and set your OpenAI API key as an environment variable:

```bash
# Windows (PowerShell)
setx OPENAI_API_KEY "sk-..."

# macOS/Linux
export OPENAI_API_KEY="sk-..."
```

---

## Folder Structure

```
repo-root/
  training/
    LabelA/
      doc1.pdf
      doc2.pdf
    LabelB/
      doc3.pdf
  documentstoclassify/
    file01.pdf
    file02.pdf

  src/ ... (solution & project files)
```

- `training/` — **required**; subfolder per label with PDFs to learn from
- `documentstoclassify/` — PDFs to be classified by KNN

You pass the **path to `training/`** as `inputData` to `RunAsync`.

---

## Configuration

The `Experiment` constructor accepts an `IConfigurationSection` and binds to your custom `MyConfig`. At minimum you’ll want:

```jsonc
// appsettings.json (example)
{
  "MyExperiment": {
    "GroupId": "ML 24/25-09",
    "AzureStorage": {
      "ConnectionString": "DefaultEndpointsProtocol=...",
      "ClassificationResultsTable": "ClassificationResults"
    }
  }
}
```

**Recommended secret handling**
- Prefer environment variables or Azure Key Vault for secrets (OpenAI key, storage keys).
- Avoid placing secrets in queue messages or source control.

---

## Inputs

### 1) Environment & Config
- `OPENAI_API_KEY` — **required**. Use secure env var in Docker/ACI.
- `MyConfig` — your configuration section (e.g., `GroupId`, storage settings).

### 2) File System
- `training/<Label>/*.pdf` — labeled training set
- `documentstoclassify/*.pdf` — documents to classify

### 3) `IExperimentRequest`
`RunAsync` receives a request object that can carry metadata and (optionally) a fallback API key. See [Queue Message Schema](#queue-message-schema).

> **Best practice:** favor `OPENAI_API_KEY` env var; keep `OpenApiKey` null unless running local tests.

---

## Outputs

1) **Classified Files**  
   Each PDF in `documentstoclassify/` is moved into a folder named by the **predicted label** via `ClassifiedFileHandler`.

2) **Azure Table Storage Records**  
   `AzureTableLogger.LogResultAsync(fileName, predictedLabel, neighbors)` writes:
   - `PartitionKey`: `MyConfig.GroupId`
   - `RowKey`: unique id
   - `InputFileName`: e.g., `resume_012.pdf`
   - `PredictedLabel`: e.g., `healthcare_worker`
   - `TopNeighborsJson`: top‑K neighbors with similarity scores

3) **Experiment Result**  
   `RunAsync` returns an `ExperimentResult` including:
   - `GroupId` (from config)
   - `StartTimeUtc`

4) **Similarity Artifacts**  
   Depending on internal settings, document & phrase similarity handlers may write CSV/JSON summaries and print console logs.

---

## Running Locally

1) **Prepare data**
```
training/<LabelA>/*.pdf
training/<LabelB>/*.pdf
documentstoclassify/*.pdf
```

2) **Configure & run**
```csharp
// Resolve configSection ("MyExperiment") and storageProvider & logger from your host app
var experiment = new MyExperiment.Experiment(configSection, storageProvider, logger);

var request = new ExperimentRequestMessage {
  ExperimentId = "exp-local-001",
  Name = "Local Run",
  Description = "KNN + Similarity"
  // OpenApiKey = null; // prefer OPENAI_API_KEY env var
};

var result = await experiment.RunAsync("./training", request);
Console.WriteLine($"GroupId: {result.GroupId}, Started: {result.StartTimeUtc:o}");
```

3) **.NET CLI**
```bash
dotnet restore
dotnet build -c Release
dotnet run --project path/to/YourHostProject
```

---

## Running with Docker

**Build**
```bash
docker build -t my-experiment:latest .
```

**Run (mount data & pass secrets)**
```bash
docker run --rm -it   -e OPENAI_API_KEY="sk-..."   -e AzureWebJobsStorage="DefaultEndpointsProtocol=..."   -v "$PWD/training:/app/training"   -v "$PWD/documentstoclassify:/app/documentstoclassify"   my-experiment:latest
```

> Adjust environment variables to your storage & config needs.

---

## Deploying to Azure Container Instances (ACI)

**Create / Update with secure env var**

```bash
# Initial create
az container create   -g <RESOURCE_GROUP>   -n <ACI_NAME>   --image <YOUR_IMAGE:TAG>   --cpu 2 --memory 4   --secure-environment-variables OPENAI_API_KEY="sk-..."   --environment-variables AzureWebJobsStorage="DefaultEndpointsProtocol=..."   --restart-policy Always
```

**Change the OpenAI key later**
```bash
# Export current template
az container export -g <RESOURCE_GROUP> -n <ACI_NAME> -f aci.yaml

# Edit aci.yaml -> containers[].properties.environmentVariables:
# - name: OPENAI_API_KEY
#   secureValue: "sk-NEW..."

# Redeploy
az container create -g <RESOURCE_GROUP> -f aci.yaml
```

> Redeploying restarts the container. Use a DNS label or front door if IP stability is required.

---

## Queue Message Schema

When triggering from a queue, send **JSON only** (no trailing code). Example:

```json
{
  "ExperimentId": "exp-2025-08-13",
  "InputFile": "https://techtweekersstorage.blob.core.windows.net/actualdocuments/grace_wilson_healthcare_worker.pdf",
  "Name": "Semantic Similarity Test 2",
  "Description": "Second Experiment with Queue",
  "MessageId": "msg124",
  "MessageReceipt": "abc457",
  "TrainingInputFilesUrl": "https://techtweekersstorage.blob.core.windows.net/trainingdocuments",
  "DocumentsToClassifyUrl": "https://techtweekersstorage.blob.core.windows.net/actualdocuments",
  "RequirementDocumentsUrl": "https://techtweekersstorage.blob.core.windows.net/requirementdocuments",
  "PhraseComparisonFilesUrl": "https://techtweekersstorage.blob.core.windows.net/phrasecomparsioncontainer",
  "OpenApiKey": null
}
```

**Server-side usage tip:** prefer
```csharp
var openAiKey = Environment.GetEnvironmentVariable("OPENAI_API_KEY")
                 ?? request.OpenApiKey; // fallback for local only
```

---

## Troubleshooting

- **Embeddings failing** → Ensure `OPENAI_API_KEY` is set & valid.  
- **No predictions** → Check that `training/` contains labeled subfolders with valid PDFs.  
- **Empty text extracted** → Your PDFs may be image-only; integrate OCR before embedding.  
- **Azure Table write fails** → Verify connection string / table name in config and network access.  
- **Container can’t see files** → If running in Docker/ACI, **mount volumes** or **download blobs** to local paths before calling `RunAsync`.

---

## Security Notes

- Keep secrets out of source & queue payloads. Use **secure env vars** or **Key Vault**.
- Limit output logging of sensitive values (keys, PII).
- Validate inbound URLs if auto-downloading from blob paths.

---

## License

Add your preferred license here (e.g., MIT, Apache-2.0).

---

## Acknowledgements

- OpenAI embeddings
- Azure Storage (Tables/Blobs)
- .NET community
