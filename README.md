# ExplainAnalyseOutput_chat
**What is ExplainAnalyseOutput?**  
ExplainAnalyseOutput is the json that contains all the metrics for different stages/operations that is generated after a query's execution.

This project is a chatbot that provides insights or analysis of the EAO json that is provided by the user. 

**Installations needed:**  
langchain:  
```pip install langchain```

streamlit:  
```pip install streamlit```

langchain_community:  
```pip install langchain_community```



Follow through:  
1) Open the file EAO_chat.py in any editor and Enter the path of EAO documentation in the appropriate place(at PyPdfLoader part).You can download the pdf of EAO documentation here [EAO_DOCUMENTATION][https://drive.google.com/file/d/1pZix9Cr62dksU2ZVRcz-SWXzPvL11K_8/view?usp=sharing]

2) open the terminal in the folder where you have the EAO_chat.py file and run the below.  
       ```streamlit run EAO_chat.py```

3) Now you will be directed to a web page. Provide the path of the folder that contains the ExplainAnalyseOutput Jsons in the box provided first and press enter.  
**Note: Provide the path of folder only irrespective of single json or mutliple jsons. Each json means one query's executions stats**  

4) Now you can start your chat!! pose your questions.  

**Note: In case you want to add/remove some jsons and make the analysis, you can simply refresh the page in browser and enter the json path again.**