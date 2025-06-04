# sentiment-scanner-bq
This is for sentiment analysis

We will be using customer reviews in a .txt file which will be uploaded to your storage bucket and the moment a new file is uploaded ,a CF will trigger and try to get the sentiment using a gen AI model and load the data in BQ for further analysis.

Here are the workflow steps:-
1) Create a storage bucket
2) Create a bq dataset followed by table
3) Update your Cloud Function with a Cloud storage trigger -> Select you bucket and keep it trigger-event-filters="type=google.cloud.storage.object.v1.finalized"
4) This trigger will invoked if you add any new file in the cloud storage bucket
5) Test your Cloud Function so that you will get rid of errors
6) Ensure your SA must have "BigQuery Data Editor or BigQuery Admin permission"
7) Just upload one response.txt file to your cloud storage bucket and your CF will invoked
8) Check your CF logs to see event are triggered or not
9) Verify data is inserted or not in BQ
   
