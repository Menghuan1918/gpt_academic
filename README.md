# DocScholar

![图片](https://github.com/Menghuan1918/gpt_academic/assets/122662527/ebeef7a8-7ef0-4c96-992d-30224f519965)


## Project Overview
The DocScholar project aims to address the dependency of students on large language models (LLMs), which often hinders independent thinking and can lead to incorrect answers due to hallucinations. We have developed a textbook-oriented knowledge base Q&A system that guides students through their textbooks rather than providing direct answers. This approach enhances critical thinking, ensures accurate learning, and ultimately fosters a deeper understanding of study materials.

## Key Features
- **Guided Thinking**: Guides students to think through information in textbooks instead of providing direct answers.
- **Retrieval-Augmented Generation (RAG) Framework**: The system first searches a large database to find the most relevant information snippets and then generates answers.
- **Categorized Support**: Answers are categorized into Class A (accurate answers) and Class B (guidance answers), providing tailored support for different types of questions.
- **Efficient Retrieval**: Combines keyword search and vector search to improve the efficiency and accuracy of information retrieval.

## Methods
We used `pdfdeal` to process PDF files into Markdown format, extracted the main content, and embedded it into the dataset via LLM. User questions are handled by the LLM through a fine-tuned model and hints. The dataset is searched using keyword and vector searches, with processed results categorized into Class A (accurate answers) and Class B (guidance answers).

## Key Findings
Our system greatly promotes independent thinking by guiding students to understand textbook content rather than providing direct answers, leading to deeper engagement with learning materials. The system ensures the accuracy and relevance of responses, reducing errors caused by hallucinations. Effective categorization into Class A (accurate answers) and Class B (guidance answers) provides tailored support for different types of questions, while the combination of keyword and vector searches improves the efficiency and precision of information retrieval.

## Usage Instructions
1. Visit our website: Scan the QR code on the poster.
2. Ask a question, and the system will guide you to find the answer through textbook content. Specific steps:
   - Enter your question.
   - Click the "Super QA" button.
