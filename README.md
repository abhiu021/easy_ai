# Tally Prime Command Processor

A Python agent that processes natural language commands related to Tally Prime and returns structured data using LangChain and LLMs.

## Features

- Classifies Tally Prime commands into root tasks and sub-tasks
- Extracts relevant parameters from natural language input
- Returns structured JSON output
- Built with LangChain for easy integration with different LLM providers

## Installation

1. Clone this repository
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the project root and add your OpenAI API key:
   ```
   OPENAI_API_KEY=your_api_key_here
   ```

## Usage

```python
from tally_agent import TallyAgent

# Initialize the agent
agent = TallyAgent()

# Process a command
command = "Show me the sales report for January 2023 for customer ABC Corp"
result = agent.process_command(command)
print(result)
```

### Example Output

```json
{
  "root_task": "Reports",
  "sub_task": "Sales",
  "parameters": {
    "company": null,
    "date_range": {
      "from": "2023-01-01",
      "to": "2023-01-31"
    },
    "filters": {
      "party": "ABC Corp"
    }
  }
}
```

## Available Root Tasks and Sub-tasks

### Master Data Access
- Ledgers
- Stock Items
- Cost Centres
- Stock Groups
- Stock Categories
- Units
- Currencies
- Price Levels
- Budgets
- Voucher Types
- Cost Categories

### Vouchers
- Sales
- Purchase
- Receipt
- Payment
- Journal
- Contra
- Debit Note
- Credit Note
- Delivery Note
- Rejections In
- Rejections Out
- Physical Stock
- Stock Journal
- Manufacturing Journal

### Reports
- Trial Balance
- Profit & Loss
- Balance Sheet
- Outstanding Reports
- Stock Summary
- GST Reports (GSTR-1, GSTR-3B, E-Way Bill Details, E-Invoice Validations)

### Import / Create Data
- Import Ledgers
- Import Stock Items
- Import Cost Centres
- Import Vouchers

### Company Info
- Company Details
- Tally Version Info
- User List
- Roles
- Connectivity Status
- Security Config
- Financial Year Info

### Advanced Functional Modules
- E-Invoice
- E-Way Bill
- Cheque Printing
- BRS Report
- Auto Bank Reconciliation
- Payroll (Salary, Deductions, Leave)
- Cost Centre Reports (Expense Analysis, Job Costing, Profitability)

## License

MIT

## Tally Prime Integration

This project integrates with Tally Prime using XML over HTTP. The following folder structure is used for Tally Prime integration:

```
tally_integration/
  ├── xml_templates/        # XML request templates for Tally
  ├── utils/               # Utilities for Tally connection and XML handling
  └── responses/           # Example/sample Tally XML responses
```

- Place reusable XML templates in `xml_templates/`.
- Implement connection and request/response logic in `utils/`.
- Store sample or test responses in `responses/`.

## Agents Folder Structure

The project organizes agent-related code as follows:

```
agents/
  ├── core/           # Core agent logic and main agent classes
  ├── prompts/        # Prompt templates for agents
  ├── utils/          # Agent-specific utility functions
  └── tests/          # Unit and integration tests for agents
```

- Place main agent logic in `core/`.
- Store prompt templates in `prompts/`.
- Add agent utilities in `utils/`.
- Write tests for agents in `tests/`.
