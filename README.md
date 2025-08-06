# LLM-Based Question Extractor for RD Sharma

This project implements a Retrieval-Augmented Generation (RAG) pipeline to extract mathematics questions from the RD Sharma Class 12 textbook and format them into clean LaTeX. This was completed as a take-home assignment for an AI Engineer role.

---

## 🚀 Approach Overview

The solution is built around a RAG pipeline using Python and the LangChain framework. It leverages Google's powerful Gemini models for both understanding the document's content and generating the final output.

The core workflow is as follows:
1.  **Document Loading**: The 795-page RD Sharma PDF is loaded and parsed using `PyMuPDF`.
2.  **Chunking**: The text is split into smaller, overlapping chunks to ensure no questions are missed and to fit within the model's context window.
3.  **Embedding & Storage**: Each text chunk is converted into a numerical vector using Google's `embedding-001` model. These embeddings are then stored in a local `FAISS` vector store, which acts as a fast, searchable index of the entire book.
4.  **Retrieval**: When the user provides a chapter and topic, the query is used to retrieve the most relevant text chunks from the FAISS index.
5.  **Generation**: A detailed prompt, the user's query, and the retrieved context are sent to Google's `gemini-1.5-flash` model. The model is instructed to identify questions only, ignore all other content, and format the output as a clean JSON list of LaTeX strings.

---

## 🛠️ How to Run

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd RD_Sharma_Extractor
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On macOS/Linux
    # venv\Scripts\activate    # On Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set your API Key:**
    Create a file named `.env` in the root directory and add your Google Gemini API key:
    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

5.  **Download the Data:**
    
    Download the RD Sharma PDF from the https://drive.google.com/file/d/1BQllRXh5_ID08uPTVfEe0DgmxPUm867F/view?usp=sharing. Place the file inside the data/ directory and ensure it is named exactly RD_Sharma_Class_12.pdf.

6.  **Run the extraction script:**
    ```bash
    python cli.py --chapter 30 --topic "Conditional Probability"
    ```
    The output will be saved in the `output/` directory as a Markdown file.

---

## 🧠 Challenges and Solutions

During development, several challenges were encountered and resolved:

* **Dependency Issues:** The initial setup faced a `ModuleNotFoundError`. This was resolved by identifying the necessary `langchain-community` package and adding it to `requirements.txt`.
* **Prompt Template Errors:** The script initially threw `ValueError`s related to the prompt structure.
    * The first error was due to a missing `{context}` variable, which was fixed by redesigning the prompt template.
    * A subsequent error was caused by the prompt's example JSON `{}` confusing Python's f-string formatting. This was solved by modifying the prompt text to escape the curly braces (`{{...}}`), ensuring they were treated as literal characters.
* **Performance Bottlenecks:** The first run was significantly longer than expected. I diagnosed this as an API rate limit on the embedding model (a common real-world constraint). To provide feedback to the user and confirm the script wasn't frozen, I integrated the `tqdm` library to display a progress bar for the embedding process, which successfully showed that the script was making steady, albeit slow, progress.

---

## 📈 Limitations & Future Work

* **Minor Over-Extraction:** The model sometimes extracts small fragments of solution text along with the question (e.g., including "Required probability = ...").
    * **Future Work:** This could be improved with more advanced prompt engineering, such as providing "negative examples" in the prompt to teach the model precisely where to stop. A two-step chain could also be implemented where a second LLM call cleans the output of the first.
* **Initial Setup Time:** The one-time cost of embedding the entire 795-page document is high due to API rate limits (15-20 minutes).
    * **Future Work:** For a production system, the FAISS index could be saved to disk after the first run and simply loaded on subsequent runs, reducing the startup time to mere seconds.