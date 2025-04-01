import os
import logging
from langchain_openai import ChatOpenAI
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def summarize_text(text, prompt_instruction, output_dir="summaries"):
    """
    Summarize text based on a specific prompt instruction.
    
    Args:
        text (str): The text to summarize
        prompt_instruction (str): The prompt with specific instructions for summarization
        output_dir (str): Directory to save the summary
    
    Returns:
        str: Path to the summary file
        str: The summarized text
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        # Generate a filename based on the first 50 chars of the prompt
        safe_prompt = "".join([c if c.isalnum() or c in [' ', '-', '_'] else '_' for c in prompt_instruction[:50]])
        summary_file = os.path.join(output_dir, f"summary_{safe_prompt}.txt")
        
        logger.info(f"Summarizing text with prompt: {prompt_instruction[:100]}...")
        
        # Split text into chunks if it's too large
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=10000,
            chunk_overlap=500,
            separators=["\n\n", "\n", ". ", " ", ""]
        )
        
        docs = [Document(page_content=t) for t in text_splitter.split_text(text)]
        
        # Initialize the LLM
        llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
        
        # Ensure the prompt incorporates the user's instruction
        map_prompt_template = f"""
        You are an expert in summarizing content.
        
        Analyze the following text based on this specific instruction:
        INSTRUCTION: {prompt_instruction}
        
        TEXT: {{text}}
        
        Based on the above instruction, extract the key information and insights.
        """
        
        combine_prompt_template = f"""
        You are an expert in creating comprehensive summaries.
        
        Your task is to create a detailed summary of the content following this specific instruction:
        INSTRUCTION: {prompt_instruction}
        
        Use the following extracted information to create a coherent, well-structured summary:
        {{text}}
        
        Your summary should be comprehensive, well-organized, and directly address the instruction.
        """
        
        # Use LangChain's summarize chain
        chain = load_summarize_chain(
            llm,
            chain_type="map_reduce",
            map_prompt=map_prompt_template,
            combine_prompt=combine_prompt_template,
            verbose=False
        )
        
        summary = chain.run(docs)
        
        # Save the summary to a file
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
            
        logger.info(f"Summary completed and saved to: {summary_file}")
        
        return summary_file, summary
        
    except Exception as e:
        logger.error(f"Error summarizing text: {str(e)}")
        raise 