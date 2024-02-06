# ExplainAnalyseOutput_chat  
 
This project is a chatbot that provides insights or analysis of the EAO json that is provided by the user. 

**What is ExplainAnalyseOutput?**  
ExplainAnalyseOutput is the json that contains all the metrics for different stages/operations that is generated after a query's execution.

**Installations needed:**  
langchain, langchain_community, streamlit:  
```pip install langchain streamlit langchain_community```

Follow through:  
1) Pull the repository , open the terminal and run the below  
       ```OPENAI_ACCESS_KEY="Your api key here" streamlit run EAO_chat.py```

2) Now you will be directed to a web page. Provide the path of the folder that contains the ExplainAnalyseOutput Jsons in the box provided first and press enter.  
**Note: Provide the path of folder only irrespective of single json or mutliple jsons. Each json means one query's executions stats**  

3) Now you can start your chat!! pose your questions.  

**Note: In case you want to add/remove some jsons and make the analysis, you can simply refresh the page in browser and enter the json path again.**