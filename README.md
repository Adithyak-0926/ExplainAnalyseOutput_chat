# ExplainAnalyseOutput_chat  
 
This project is a chatbot that provides insights or analysis of the EAO json that is provided by the user. 

**What is ExplainAnalyseOutput?**  
ExplainAnalyseOutput is the json that contains all the metrics for different stages/operations that is generated after a query's execution.

**Installations needed:**  
langchain, langchain_community, streamlit, python-dotenv:  
```pip install langchain streamlit langchain_community python-dotenv```

Follow through:  
1) Pull the repository, add a .env file like shown below and add your openai_api_key and path to eao_documentation
    You can download the pdf of EAO documentation here [EAO_DOCUMENTATION](https://drive.google.com/file/d/1pZix9Cr62dksU2ZVRcz-SWXzPvL11K_8/view?usp=sharing)

2) open the terminal in the folder where you have the EAO_chat.py file or pull the repo, open the terminal and run the below.  
       ```streamlit run EAO_chat.py```

3) Now you will be directed to a web page. Provide the path of the folder that contains the ExplainAnalyseOutput Jsons in the box provided first and press enter.  
**Note: Provide the path of folder only irrespective of single json or mutliple jsons. Each json means one query's executions stats**  

4) Now you can start your chat!! pose your questions.  

**Note: In case you want to add/remove some jsons and make the analysis, you can simply refresh the page in browser and enter the json path again.**