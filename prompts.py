assistant_instructions = """
"You are an AI assistant specialising in information retrieval and analysis. Do a detailed analysis and return a result in a text format with no markdown formattings. Always give short and concised reply, the answer should be one liner whenever possible, otherwise it should use as less lines as possible."
"Response structure, return a string with html tags used to format the response use tags like list tags, <b> and <u> and other tags. if neccessary"
For every answer, analyse all the given information completely and give a very appropriate concised answer for the given question.
For every answer, always provide the source(page number from which the answer is gathered).
"""

questions = [
    "What is the Bid Department/Title of the work/Company Name that is providing this tender?",
    "What is the Name of the Work from the given information? Analyse all the information given get a appropriate name of the work.",
    "What is the Bid Platform/Mode of the bid?",
    "What is the Bid Type: is the bid type online or offline?",
    "What is the Prebid meeting date and location, and is there any meeting link provided?",
    "What are the Contact Person/Details for any clarification given in the information?",
    "What is the Bid Open date from the given information?",
    "What is the Bid Close date from the given information?",
    "What is the Project Completion Period from the given information?",
    "What are the Bidder eligibility criteria/Prequalification criteria, and are there any supporting documents required?",
    "What is the Detailed Scope of Contract/Work?",
    "What is the AMC required, if any?",
    "What is the Detailed Technical data BOQ from the BID, like Type of panels, Specification/Type of inverter, and type of structure, etc.?",
    "What is the Estimated bid value/project value?",
    "What is the EMD AMOUNT?",
    "What is the EMD exception, if any: check the information provided perfectly and tell if there are any exceptions in EMD?",
    "What is the Security deposit/Bank guarantee/SBG?",
    "What are the Payment terms/Terms of payment/Payment mode?",
    "What are the Penalty clauses, if any: check if there are any penalty clauses?",
    "What are the mandatory clauses in the given tender/bid information?",
    "What are the safety clauses in the given tender/bid information?",
    "What is the summary of the key findings from your analysis, and what are your recommendations based on those findings?"

    
]