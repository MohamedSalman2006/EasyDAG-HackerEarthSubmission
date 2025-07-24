# EasyDAG: The Conversational BlockDAG Assistant

A submission for the BlockDAG Hackathon 2025.

## Overview

EasyDAG is a web application designed to make smart contract development on BlockDAG accessible to everyone. While blockchain technology can be complex for newcomers, our project significantly lowers this barrier with a dual-mode AI assistant. This allows both beginners and experts to generate, understand, and discuss smart contracts using natural language. 

---

## Key Highlights

#### Dual-Mode AI Assistance 
The contract generator can be switched between two convenient modes: 
* **Conversational Mode:** Chat with a friendly, knowledgeable AI powered by Google Gemini 1.5 Flash to ask questions about BlockDAG and smart contracts in plain English. 
* **Protocol Builder Mode:** Generate secure, ready-to-use smart contract templates using a clean, form-based interface with no coding experience required. 

#### Multi-Contract Support 
Build three essential contract types out-of-the-box: 
* ERC-20 Tokens 
* Staking Protocols 
* Vesting Contracts 

#### Interactive Community 
EasyDAG features a dynamic community forum where users can post questions, create blog entries, upvote or downvote posts, and collaborate with others.

#### Secure Wallet & Guest Authentication 
The user-friendly interface includes auto-expanding chat inputs, hover-to-preview contract templates, and dynamic forms that adapt to your choices for a clean, responsive experience.

---

## 🛠️ Our Technology Stack 

| Layer | Technology |
| :--- | :--- |
| **Backend** | Django, Django REST Framework |
| **AI & Agents**| Google Gemini 1.5 Flash, LangGraph, LangChain |
| **Database** | SQLite (for local development) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Authentication**| JWT (via `simple-jwt`), MetaMask signature verification |

---

## How to Use This? 

Follow these instructions to set up EasyDAG locally.

**Prerequisites:**
* Python 3.10+ 
* Pip (Python Package Manager)
* Venv (Python Virtual Environments)
### Setup Guide 

1.  **Clone the Repository** 
    ```bash
    git clone [YOUR-GITHUB-REPO-LINK]
    cd your-repo-name
    ```
    

2.  **Navigate to the Backend** 
    ```bash
    cd backend/backendCore
    ```
    

3.  **Create & Activate a Virtual Environment** 
    * For Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
     
    * For macOS/Linux: 
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
      

4.  **Install Python Dependencies** 
    ```bash
    pip install -r requirements.txt
    ```
    

5.  **Set Up Environment Variables** 
    Create a `.env` file in the `backendCore` directory and add your keys: 
    ```
    GEMINI_API_KEY=AiSy234...Your...SecretApiKey
    SECRET_KEY=1234...Your...DjangoSecretKey
    DEBUG=True
    ```
    

6.  **Run Database Migrations** 
    ```bash
    python manage.py migrate
    ```
   
7.  **Start the Server** 
    ```bash
    python manage.py runserver
    ```
    
    Visit `http://127.0.0.1:8000` to access the application. 

---

## Using EasyDAG 

1.  **Login:** Connect your MetaMask wallet for secure authentication or "Continue as Guest" to explore all features without an account. 
2.  **Chat with AI:** On the Contracts page, use the conversational chat bar to ask the AI anything about BlockDAG.
3.  **Build Smart Contracts:** Switch to "Protocol Builder" mode to open the guided form. Select the contract type, fill in the details, and click "Generate" to view your secure, ready-made smart contract. 
4.  **Join the Community:** Visit the community tab to post questions or blogs, vote on posts, and share knowledge. 

---

## Our Team 

* **Mohamed Salman** - Project Lead, Backend Dev, DB Arch 
* **Suresh Krishnan** - Frontend Dev 
* **Sri Shineka SK** - ML Finetuning
* **Aswin Kumar** - UI/UX Designing 
* **Haanika Ishani** - Assist 