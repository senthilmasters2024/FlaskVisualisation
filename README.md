# ML 24/25-09 Semantic Similarity Analysis of Textual Data - Azure Cloud Implementation

## Contents

- [Introduction](#intro)
- [Inputs and Outputs](#inputoutput)
- [Experimental Flow of SE project](#seproj)
- [Experiment Execution on Azure](#azureproj)
- [How to run the experiment](#run)
- [Observation](#obsrvtn)
- [Conclusion](#concln)

<a name="intro"></a>

## Introduction

This project focuses on analyzing semantic similarity between documents and phrases using OpenAI embeddings, KNN classification, and Azure-based infrastructure. The system performs preprocessing (including lemmatization and stopword removal), generates text embeddings, classifies documents, compares them across domains, and stores results in Azure Table and Blob storage. It is built using C# .NET 8, fully Dockerized, and integrated with Azure Queue triggers and cloud containers.

To enable scalable deployment, the application has been containerized with Docker and integrated into a cloud-native workflow on Microsoft Azure. The solution uses Azure Container Registry and Azure Container Instances for hosting and execution, while message queue-based input processing ensures asynchronous, efficient data handling. Resulting similarity outputs are stored in Azure Blob Storage, and system performance is monitored using Azure observability tools. This cloud-based architecture supports robust, real-time document comparison and serves as a foundation for future enhancements in NLP-driven applications.

[SE Project Documentation PDF link](https://github.com/senthilmasters2024/Tech_Tweakers/blob/main/SemanticAnalysisTextualData/SemanticAnalysisTextualData/Documentation/SemanticSimilarityAnalysisTextualData.pdf)

<a name="inputs-and-outputs"></a>

 Inputs and Outputs


## Inputs and Outputs

### Input:

The Semantic Similarity Analysis system accepts three types of textual inputs: individual words, phrases, and full-length documents. Inputs are organized into two main folders, which contains source documents used as references, and the other one which holds the target documents to be compared. Each source document is evaluated against one or more target documents to determine semantic similarity. For document-level comparisons, inputs must be in plain .txt format, while phrase-level comparisons can be provided via CSV files.The experiment is designed to accept a variety of input types depending on the analysis being performed. Once the inputs are received in the Azure-hosted container instance(via Docker and Azure Container Registry), they are processed and embedded using OpenAI's embedding API. Final similarity outputs are stored in Azure Blob Storage for further analysis, while application health and performance are monitored through integrated Azure diagnostics. This cloud-integrated input pipeline enables real-time, scalable semantic analysis across diverse datasets with minimal manual intervention.

missing: Image

### Output: 

Primary outputs include CSV files containing document-level similarity scores (e.g., cosine similarity), phrase-level similarity results using OpenAI embeddings, and predicted classification labels based on the KNN algorithm. In parallel, structured results are logged into Azure Table Storage across tables like ClassificationResults,DocumentSimilarityResults, and PhraseSimilarityResults to support efficient querying and analysis. All output files, including CSVs and optional embeddings, are uploaded to Azure Blob Storage for centralized access and integration with other cloud services. This setup ensures the results are both easy to interpret and ready for further automated processing or evaluation.

missing: Add Image

3. What your algorithmas does? How ?

<a name="workflow"></a>

## Experimental Flow of SE Project

A brief step by step description of the SE project is as follows:

### 1. Input Processing

Downloads training, test, requirement, and phrase documents from Azure Blob containers.The raw data is later preprocessed by applying tokenization, lemmatization, stopword filtering, and language detection.

### 2. Embedding Generation
To handle long inputs, we split text into ~3000-character chunks and embed each with OpenAI text-embedding-3-large, then average the vectors into a single representation: OpenAIEmbeddingService.GetEmbeddingAsync powers training/classification, whereas SemanticSimilarityForDocumentsWithInputDataDynamic.GetAveragedEmbeddingAsync is used for document similarity. This is done by using the following :

```csharp

// MyExperiment/Services/OpenAIEmbeddingService.cs
public async Task<float[]> GetEmbeddingAsync(string text)

```

### 3. Classification with KNN
PDFs are classified using K-Nearest Neighbors based on embedding similarity. Classified PDFs are grouped and saved into folders.The below code is the core logic of this classification. 

```csharp

// Create the classifier with training data and k=3
var knn = new KNNClassifier(trainingData, k: 3);
// Initialize the PDF reader to extract text from training and test documents
var pdfReader = new PdfReaderService();
// Initialize the OpenAI embedding service with the chosen model and API key
var embeddingService = new OpenAIEmbeddingService("text-embedding-3-large", openAIKey);

// Load and embed training data (from training folder downloaded as blob) and return it as a list of labeled vectors
var trainingData = await LoadTrainingDataAsync(pdfReader, embeddingService, inputData,request);

// Train the K-Nearest Neighbors classifier using the embedded training data
var knn = new KNNClassifier(trainingData, k: 3);

// Classify the test files using the trained KNN classifier
await ClassifyTestFilesAsync(pdfReader, embeddingService, knn);

```

### 4. Document Comparison
Requirement docs vs classified docs are compared within shared domains.Similarity is calculated (Cosine Similarity), and results are logged.

### 5. Phrase Similarity
Phrases from input CSV are embedded and compared.Results are saved as CSV and pushed to Azure Tables.

### 6. Result Upload
CSV files are uploaded to Azure Blob. Metadata and logs are written to Azure Tables.


<a name="execution-on-azure"></a>

## Experiment Execution on Azure

### 1. create an Azure Container registry (ACR)

"image can be added"

### 2. Add Docker support and build image locally

```bash

docker build -t mycloudproject 

```


### 3. Login to ACR and push the image

```bash

# log in to Azure and to ACR
az login
az acr login -n $ACR

# find your local image
docker images

# tag & push
docker tag mycloudproject:latest $ACR.azurecr.io/mycloudproject:v1
docker push $ACR.azurecr.io/mycloudproject:v1

```

### 4. Create an Azure storage accout and the required blob containers

```bash


```
The follwing containers have been cretaed 

a) trainingdocuments

b) actualdocuments

c) requirementdocuments

d) phrasecomparsioncontainer

e) classifiedoutput, documentembeddings  (Outputs written by code) 

### 5. Upload Input Files to Azure Blob Storage(Containers)

The following C# code is used to upload inputs :

```csharp

using Azure.Storage.Blobs;
using System;
using System.IO;

// Connection string to your Azure Storage Account
string connectionString = _config.StorageConnectionString; // or Environment.GetEnvironmentVariable("AZURE_STORAGE_CONNECTION_STRING")

// Container where training input files are stored
string containerName = "trainingdocuments"; // same as MyConfig.TrainingContainer

// Category folder in the container (MUST match appsettings MyConfig.TrainingCategoryFolders)
string category = "developerprofiles"; // e.g., "developerprofiles", "devopsprofiles", "healthcareprofiles"

// Path to the local file to upload
string filePath = @"C:\data\training\resume1.pdf"; // change to your file

// Create a BlobServiceClient
BlobServiceClient blobServiceClient = new BlobServiceClient(connectionString);

// Get a reference to the container and create it if it doesn't exist
BlobContainerClient containerClient = blobServiceClient.GetBlobContainerClient(containerName);
await containerClient.CreateIfNotExistsAsync();

// Get a reference to the blob (CATEGORY PREFIX + file name)
string fileName = Path.GetFileName(filePath);
string blobName = $"{category}/{fileName}";
BlobClient blobClient = containerClient.GetBlobClient(blobName);

// Upload the file
await blobClient.UploadAsync(filePath, overwrite: true);

Console.WriteLine($"File '{fileName}' uploaded to '{containerName}/{blobName}'.");



```

### 5. Send Queue Message (trigger-queue).

The trigger-queue (from appsettings.json) signals the container to start processing. 

Example queue message (JSON):
```json

{
  "ExperimentId": "ML 24/25-09",
  "InputFile": "https://techtweekersstorage.blob.core.windows.net/trainingdocuments/inputDataset.csv",
  "Name": "Semantic Similarity Processing",
  "Description": "Runs document preprocessing and similarity calculations",
  "MessageId": "msg-01",
  "MessageReceipt": "receipt-token"
}
```


### 7. Message Reception (ReceiveExperimentRequestAsync)

The input file is downloaded locally for processing.

When a message arrives in the queue, it is received and deserialized. 
The following code from IStorageProvider in MyCloudProject.Common performs this:

```csharp

public async Task<IExerimentRequest> ReceiveExperimentRequestAsync(CancellationToken token)
{
    // 1. Create a QueueClient to connect to the Azure Storage Queue
    //    using the connection string and queue name from configuration.
    _queueClient = new QueueClient(_config.StorageConnectionString, _config.Queue);

    // 2. Ensure the queue exists (creates it if not).
    await _queueClient.CreateIfNotExistsAsync();

    // 3. Receive available messages from the queue.
    QueueMessage[] messages = await _queueClient.ReceiveMessagesAsync();

    // 4. If there are messages, process the first one.
    if (messages.Length > 0)
    {
        // 4.1 Convert the message body to string.
        string msgTxt = messages[0].Body.ToString();

        // 4.2 Deserialize the message into an experiment request object.
        var request = JsonSerializer.Deserialize<ExerimentRequestMessage>(msgTxt);

        // 4.3 Store the message ID and receipt (needed for deletion later).
        request.MessageId = messages[0].MessageId;
        request.MessageReceipt = messages[0].PopReceipt;

        // 4.4 Return the populated request.
        return request;
    }

    // 5. If no messages are available, return null.
    return null;
}

```

### 8. Input Download (DownloadInputAsync)

This method downloads the input file from Azure Blob Storage to a local folder for processing.

```csharp

public async Task<string> DownloadInputAsync(string fileName, IExperimentRequest request)
{
    // 1. Initialize the BlobContainerClient for the training container
    //    using the connection string from configuration.
    BlobContainerClient container = new BlobContainerClient(
        _config.StorageConnectionString, 
        _config.TrainingContainer
    );

    // 2. Define a local folder path to store downloaded files.
    string localPath = Path.Combine(Directory.GetCurrentDirectory(), "DownloadedFiles");

    // 3. Create the folder if it does not already exist.
    Directory.CreateDirectory(localPath);

    // 4. Get a BlobClient reference for the specific file (use only the file name).
    BlobClient blob = container.GetBlobClient(Path.GetFileName(fileName));

    // 5. Define the full local path where the file will be saved.
    string downloadPath = Path.Combine(localPath, Path.GetFileName(fileName));

    // 6. Download the file from Azure Blob Storage to the local path.
    await blob.DownloadToAsync(downloadPath);

    // 7. Return the local file path for further processing.
    return downloadPath;
}

```


### 9. Retrieve Results 
The experiment logic is invoked from Program.cs as shown belw:

```csharp

IExperimentResult result = await experiment.RunAsync(localFileWithInputArgs);

```
### 10. Upload Output (UploadResultAsync)

```csharp

public async Task UploadResultAsync(string experimentName, IExperimentResult result, DateTime starttime, IExperimentRequest request)
{
    // 1. Create a Blob container client for storing results.
    BlobContainerClient container = new BlobContainerClient(
        _config.StorageConnectionString, 
        _config.ClassifiedDocuments
    );

    // 2. Create the container if it does not exist.
    await container.CreateIfNotExistsAsync();

    // 3. Upload the output file using the experiment name.
    using FileStream fileStream = File.OpenRead(result.OutputFile);
    await container.UploadBlobAsync($"{experimentName}.csv", fileStream);
}

```

### 11. Store Results in Table Storage

Experiment metadata and output URLs are saved in the "ClassificationResults" table.

image???

### 12. Commit Queue Message (CommitRequestAsync)

The processed queue message is deleted to prevent reprocessing. 
The below code is used:

```csharp

public async Task CommitRequestAsync(IExerimentRequest request)
{
    // 1. Connect to the Azure Queue using the configured connection string and queue name.
    QueueClient queueClient = new QueueClient(
        _config.StorageConnectionString, 
        _config.Queue
    );

    // 2. Delete the message using its ID and receipt to confirm completion.
    await queueClient.DeleteMessageAsync(
        request.MessageId, 
        request.MessageReceipt
    );
}

```

### 13 . Output related missing



<a name="running-experiment"></a>

## How to run experiment  (check please)
1. Ensure input folders are uploaded to their respective containers:

a. trainingdocuments

b. actualdocuments

c. equirementdocuments

d. phrasecomparsioncontainer

2. Start ACI or run locally via Visual Studio/Docker.

Start the worker (ACI/Docker/Visual Studio), ensuring OPENAI_API_KEY is set and the config file is picked up (your env key is MYCLOUDPROJECT_ENVIRONMENT=Developement to match appsettings.Developement.json) 

3. Submit a trigger message to Azure Queue.
Send a trigger message (plain JSON or Base64 JSON) to the trigger-queue with fields like ExperimentId, Name, Description (and optional InputFile)

4. Results will be saved to:

a. documentembeddings

b. classifiedoutput

c. result-tables (Azure Tables)

Describe Your Cloud Experiment based on the Input/Output you gave in the Previous Section.


### Observation

The label distribution across domains is roughly balanced with a small skew, and the PCA (2D/3D) projections show compact, well-separated clusters by domain, with only a few boundary points drifting toward other groups. Top-K neighbor views are dominated by same-domain matches with high cosine scores, and the per-dimension component traces for paired documents follow similar shapes, indicating that the embedding signal is not overwhelmed by noise. Ranked-similarity charts display a visible gap between the highest and lowest scores, giving a natural cutoff to accept matches or flag them for review. Operationally, the pipeline is populating the expected blobs and tables (inputs in the source containers; outputs in documentembeddings/ and classifieddocuments/; run metadata and scores in the Azure Tables).

<p align="center">
  <img src="./Images/Document Embedding-PCA.jpeg" alt="Results table" width="60%">

<p align="center">
  <img src="./Images/PCA-2D-3D.jpeg" alt="Results table" width="60%">
 
### Conclusion 

The end-to-end workflow (Blob → embeddings → KNN → similarity → Tables/Blobs) is working as intended, and the OpenAI embeddings are sufficiently discriminative for these domains, making KNN a solid baseline. A practical acceptance threshold can be derived from the ranked-similarity elbow; items below that line should be queued for manual check. To improve robustness, balance under-represented classes, add hard negatives (near-miss cross-domain docs), and watch text extraction quality from PDFs. Keep caching embeddings to avoid recompute, monitor the Azure Tables for drift, and version runs via ExperimentMetadata for reproducibility.



