import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
from google import genai
from concurrent.futures import TimeoutError
from functools import partial

# Load environment variables from .env file
load_dotenv()

# Access your API key and initialize Gemini client correctly
api_key = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# ============================================================
# CONFIGURATION - UPDATE THESE VALUES
# ============================================================
RECIPIENT_EMAIL = "your.email@example.com"  # TODO: Replace with actual email
# ============================================================

max_iterations = 3
last_response = None
iteration = 0
iteration_response = []

async def generate_with_timeout(client, prompt, timeout=10):
    """Generate content with a timeout"""
    print("Starting LLM generation...")
    try:
        loop = asyncio.get_event_loop()
        response = await asyncio.wait_for(
            loop.run_in_executor(
                None, 
                lambda: client.models.generate_content(
                    model="gemini-2.0-flash-lite",
                    contents=prompt
                )
            ),
            timeout=timeout
        )
        print("LLM generation completed")
        return response
    except TimeoutError:
        print("LLM generation timed out!")
        raise
    except Exception as e:
        print(f"Error in LLM generation: {e}")
        raise

def reset_state():
    """Reset all global variables to their initial state"""
    global last_response, iteration, iteration_response
    last_response = None
    iteration = 0
    iteration_response = []

async def main():
    reset_state()
    print("Starting main execution...")
    
    try:
        # Create connections to BOTH MCP servers
        print("\n" + "="*60)
        print("Establishing connections to MCP servers...")
        print("="*60)
        
        # Server 1: Calculator/Paint server
        calc_server_params = StdioServerParameters(
            command="python",
            args=["mcp_server.py"]
        )
        
        # Server 2: Gmail server
        gmail_server_params = StdioServerParameters(
            command="python",
            args=["gmail_mcp_server.py"]
        )
        
        # Connect to both servers
        async with stdio_client(calc_server_params) as (calc_read, calc_write), \
                   stdio_client(gmail_server_params) as (gmail_read, gmail_write):
            
            print("✓ Connected to both servers")
            
            # Create sessions for both servers
            async with ClientSession(calc_read, calc_write) as calc_session, \
                       ClientSession(gmail_read, gmail_write) as gmail_session:
                
                print("✓ Sessions created")
                
                # Initialize both sessions
                await calc_session.initialize()
                await gmail_session.initialize()
                print("✓ Sessions initialized")
                
                # Get tools from both servers
                calc_tools_result = await calc_session.list_tools()
                calc_tools = calc_tools_result.tools
                print(f"✓ Calculator server: {len(calc_tools)} tools")
                
                gmail_tools_result = await gmail_session.list_tools()
                gmail_tools = gmail_tools_result.tools
                print(f"✓ Gmail server: {len(gmail_tools)} tools")
                
                # Combine all tools
                all_tools = list(calc_tools) + list(gmail_tools)
                print(f"✓ Total tools available: {len(all_tools)}")
                print("="*60 + "\n")
                
                # Create a mapping of tool names to sessions
                tool_to_session = {}
                for tool in calc_tools:
                    tool_to_session[tool.name] = calc_session
                for tool in gmail_tools:
                    tool_to_session[tool.name] = gmail_session
                
                # Create tools description
                tools_description = []
                for i, tool in enumerate(all_tools):
                    try:
                        params = tool.inputSchema
                        desc = getattr(tool, 'description', 'No description available')
                        name = getattr(tool, 'name', f'tool_{i}')
                        
                        # Format the input schema
                        if 'properties' in params:
                            param_details = []
                            for param_name, param_info in params['properties'].items():
                                param_type = param_info.get('type', 'unknown')
                                param_details.append(f"{param_name}: {param_type}")
                            params_str = ', '.join(param_details)
                        else:
                            params_str = 'no parameters'
                        
                        tool_desc = f"{i+1}. {name}({params_str}) - {desc}"
                        tools_description.append(tool_desc)
                        print(f"Added tool: {name}")
                    except Exception as e:
                        print(f"Error processing tool {i}: {e}")
                        tools_description.append(f"{i+1}. Error processing tool")
                
                tools_description = "\n".join(tools_description)
                print("\n✓ Tools description created\n")
                
                # Create system prompt with Gmail integration
                system_prompt = f"""You are a math agent solving problems in iterations. You have access to various mathematical, visualization, and email tools.

Available tools:
{tools_description}

You must respond with EXACTLY ONE line in one of these formats (no additional text):
1. For function calls:
   FUNCTION_CALL: function_name|param1|param2|...

Important:
- When a function returns multiple values (like arrays), you need to process all of them
- When passing arrays as parameters, use comma-separated values: value1,value2,value3
- After calculating the final answer, you MUST:
  1. Visualize it in Paint using this sequence:
     * First call: open_paint_and_select_rectangle|rect_tool_x|rect_tool_y (e.g., open_paint_and_select_rectangle|530|85)
       - This opens Paint, maximizes it, and clicks the rectangle tool
       - CALL THIS ONLY ONCE
     * Second call: draw_rectangle|x1|y1|x2|y2 (e.g., draw_rectangle|250|250|1702|922)
       - This draws the rectangle by clicking and dragging from (x1,y1) to (x2,y2)
     * Third call: add_text_in_paint|your_final_answer (e.g., add_text_in_paint|FINAL_ANSWER: [42])
       - This adds text inside the rectangle
  2. Send the result via email:
     * Final call: send_email|{RECIPIENT_EMAIL}|Calculation Result|Your final answer message
       - Example: send_email|{RECIPIENT_EMAIL}|INDIA ASCII Sum Result|The exponential sum is: 1.234e56
- Do not repeat function calls with the same parameters

Examples:
- FUNCTION_CALL: strings_to_chars_to_int|INDIA
- FUNCTION_CALL: int_list_to_exponential_sum|73,78,68,73,65
- FUNCTION_CALL: open_paint_and_select_rectangle|530|85
- FUNCTION_CALL: draw_rectangle|250|250|1702|922
- FUNCTION_CALL: add_text_in_paint|FINAL_ANSWER: [42]
- FUNCTION_CALL: send_email|{RECIPIENT_EMAIL}|Calculation Complete|Final answer: 42

DO NOT include any explanations or additional text.
Your entire response should be a single line starting with FUNCTION_CALL:"""

                query = """Find the ASCII values of characters in INDIA and then return sum of exponentials of those values. After getting the final answer, display it in Paint and send the result via email."""
                
                print(f"Query: {query}\n")
                
                # Use global iteration variables
                global iteration, last_response
                
                # Increase max iterations to allow for Paint + Email operations
                max_iterations_extended = 12
                executed_calls = set()
                current_query = query
                
                while iteration < max_iterations_extended:
                    print(f"\n{'='*60}")
                    print(f"ITERATION {iteration + 1}")
                    print(f"{'='*60}")
                    
                    if last_response is not None:
                        current_query = current_query + "\n\n" + " ".join(iteration_response)
                        current_query = current_query + "  What should I do next?"
                    
                    # Get model's response with timeout
                    prompt = f"{system_prompt}\n\nQuery: {current_query}"
                    try:
                        response = await generate_with_timeout(client, prompt)
                        response_text = response.text.strip()
                        print(f"LLM Response: {response_text}")
                        
                        # Find the FUNCTION_CALL or FINAL_ANSWER line
                        for line in response_text.split('\n'):
                            line = line.strip()
                            if line.startswith("FUNCTION_CALL:") or line.startswith("FINAL_ANSWER:"):
                                response_text = line
                                break
                    
                    except Exception as e:
                        print(f"Failed to get LLM response: {e}")
                        break
                    
                    if response_text.startswith("FUNCTION_CALL:"):
                        _, function_info = response_text.split(":", 1)
                        parts = [p.strip() for p in function_info.split("|")]
                        func_name, params = parts[0], parts[1:]
                        
                        print(f"\n>>> Function: {func_name}")
                        print(f">>> Parameters: {params}")
                        
                        # Prevent duplicates
                        call_signature = f"{func_name}|{'|'.join(params)}"
                        if call_signature in executed_calls:
                            print(f"⚠️  Skipping duplicate call: {call_signature}")
                            iteration_response.append(f"Skipped duplicate call: {call_signature}")
                            iteration += 1
                            continue
                        
                        executed_calls.add(call_signature)
                        
                        try:
                            # Find the matching tool and session
                            tool = next((t for t in all_tools if t.name == func_name), None)
                            if not tool:
                                print(f"❌ Unknown tool: {func_name}")
                                raise ValueError(f"Unknown tool: {func_name}")
                            
                            # Get the correct session for this tool
                            session = tool_to_session[func_name]
                            
                            # Prepare arguments
                            arguments = {}
                            schema_properties = tool.inputSchema.get('properties', {})
                            
                            for param_name, param_info in schema_properties.items():
                                if not params:
                                    raise ValueError(f"Not enough parameters for {func_name}")
                                
                                value = params.pop(0)
                                param_type = param_info.get('type', 'string')
                                
                                # Convert to correct type
                                if param_type == 'integer':
                                    arguments[param_name] = int(value)
                                elif param_type == 'number':
                                    arguments[param_name] = float(value)
                                elif param_type == 'array':
                                    if isinstance(value, str):
                                        value = value.strip('[]').replace(' ', '')
                                        value_list = value.split(',')
                                        try:
                                            arguments[param_name] = [int(x) for x in value_list if x]
                                        except ValueError:
                                            try:
                                                arguments[param_name] = [float(x) for x in value_list if x]
                                            except ValueError:
                                                arguments[param_name] = [x for x in value_list if x]
                                    else:
                                        arguments[param_name] = value
                                else:
                                    arguments[param_name] = str(value)
                            
                            print(f">>> Calling: {func_name}({arguments})")
                            
                            # Call the tool on the correct session
                            result = await session.call_tool(func_name, arguments=arguments)
                            
                            # Print result
                            if hasattr(result, 'content') and result.content:
                                first_content = result.content[0]
                                if hasattr(first_content, 'text'):
                                    print(f">>> Result: {first_content.text}")
                                else:
                                    print(f">>> Result: {str(first_content)}")
                            else:
                                print(f">>> Result: {str(result)}")
                            
                            # Get the full result content
                            iteration_result = ""
                            if hasattr(result, 'content'):
                                if isinstance(result.content, list):
                                    iteration_result_list = []
                                    for item in result.content:
                                        if hasattr(item, 'text'):
                                            iteration_result_list.append(item.text)
                                        else:
                                            iteration_result_list.append(str(item))
                                    iteration_result = iteration_result_list
                                else:
                                    iteration_result = str(result.content)
                            else:
                                iteration_result = str(result)
                            
                            # Format response
                            if isinstance(iteration_result, list):
                                result_str = ','.join(str(x) for x in iteration_result)
                                result_display = f"[{result_str}]"
                            else:
                                result_str = str(iteration_result)
                                result_display = result_str
                            
                            iteration_response.append(
                                f"In iteration {iteration + 1} you called {func_name} with {arguments} parameters, "
                                f"and the function returned {result_display}. "
                                f"To use this result in the next function call with an array parameter, use: {result_str}"
                            )
                            last_response = iteration_result
                        
                        except Exception as e:
                            print(f"❌ Error: {str(e)}")
                            import traceback
                            traceback.print_exc()
                            iteration_response.append(f"Error in iteration {iteration + 1}: {str(e)}")
                            break
                    
                    elif response_text.startswith("FINAL_ANSWER:"):
                        print("\n" + "="*60)
                        print("AGENT EXECUTION COMPLETE")
                        print("="*60)
                        print(f"Final answer: {response_text}")
                        iteration_response.append(f"Agent completed with: {response_text}")
                        break
                    
                    else:
                        print(f"⚠️  Unexpected response format: {response_text}")
                        break
                    
                    iteration += 1
                
                print("\n" + "="*60)
                print("EXECUTION FINISHED")
                print(f"Total iterations: {iteration}")
                print("="*60)
    
    except Exception as e:
        print(f"❌ Error in main execution: {e}")
        import traceback
        traceback.print_exc()
    finally:
        reset_state()

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MULTI-SERVER MCP AGENT WITH GMAIL INTEGRATION")
    print("="*60)
    print(f"Recipient Email: {RECIPIENT_EMAIL}")
    print("="*60 + "\n")
    
    if RECIPIENT_EMAIL == "your.email@example.com":
        print("⚠️  WARNING: Please update RECIPIENT_EMAIL in this file!")
        print("="*60 + "\n")
    
    asyncio.run(main())
