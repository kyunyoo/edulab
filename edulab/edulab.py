# 유태균 노트:
# 시간적 개념을 저장 시스템에 구현해야될 필요가 있음 to get the sense of time in memory stream(뭐가 먼저 저장된 메모리인가) 그래야지 LLM이 고려를 하고 답변을 생성하지
# 일단 전체적으로 api call을 부를때 마다 답장해주는 방식이 다름--> 그래서 메모리 스트림에 저장할때 좀 더 효율적으로 정리하게 하는 방법이 고안될 필요가 있어보임.
# 리트리벌을 중요한거를 뽑아오지 않기때문에 중요한 메모리에는 표기를 해서 저장해야될 필요가 있어보임.
# 마지막 agreement를 어떤식으로 뽑을지 고민을 해볼 필요가 있음.
import openai
import csv

# Initialize OpenAI API key
openai.api_key = "여기다 api key"

def gpt_api_call(messages):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return response.choices[0].message['content'].strip()

# Define the Agent class
class Agent:
    def __init__(self, name, goal):
        self.name = name
        self.goal = goal
        self.memory = []

    def save_memory(self, conversation):
        self.memory.append(conversation)

    def plan(self):
        memory_context = "\n".join([f"{self.name}: {mem}" for mem in self.memory])
        plan_prompt = {"role": "system", "content": f"{self.name} with the goal of {self.goal}, what should be the next action to solve the problem?"}
        plan_response = gpt_api_call([{"role": "system", "content": memory_context}, plan_prompt])
        self.save_memory(f"Plan: {plan_response}")
        return plan_response

    def respond(self, prompt, other_agent_name):
        memory_context = "\n".join([f"{self.name}: {mem}" for mem in self.memory])
        full_prompt = [
            {"role": "system", "content": memory_context},
            {"role": "user", "content": f"{other_agent_name}: {prompt}"},
            {"role": "assistant", "content": f"{self.name}: {self.goal}"}
        ]
        response = gpt_api_call(full_prompt)
        self.save_memory(f"{self.name}: {response}")
        return response

    def reflect(self):
        memory_context = "\n".join([f"{self.name}: {mem}" for mem in self.memory])
        reflection_prompt = {"role": "system", "content": f"{self.name}, based on our discussion so far, please provide two higher-level reflections on our progress and strategy."}
        reflection_response = gpt_api_call([{"role": "system", "content": memory_context}, reflection_prompt])
        self.save_memory(f"Reflection: {reflection_response}")
        return reflection_response

    def finalize_agreement(self, prompt):
        memory_context = "\n".join([f"{self.name}: {mem}" for mem in self.memory])
        full_prompt = [
            {"role": "system", "content": memory_context},
            {"role": "user", "content": f"{self.name}: {prompt}"}
        ]
        response = gpt_api_call(full_prompt)
        self.save_memory(f"Final Agreement: {response}")
        return response

# Function to save memory to a CSV file
def save_memory_to_csv(filename, memory):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Memory'])
        for item in memory:
            writer.writerow([item])

# Function to save responses to a CSV file
def save_responses_to_csv(filename, responses):
    with open(filename, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Agent', 'Response'])
        for response in responses:
            writer.writerow(response)

# Initialize agents with specific goals
agent1 = Agent("Agent1", "achieving the highest power output")
agent2 = Agent("Agent2", "achieving the lowest level of negative environmental impact")

# Problem to solve
problem = """
one student is focused on achieving the highest power output (Power condition), and the other is focused on achieving the lowest level of negative environmental impact (Green condition). They must agree on a single design while meeting their individual objectives.
"""

# Initial conversation starter
conversation = problem

# List to keep track of responses
responses = []

# Conversation loop
for i in range(9):
    # Plan and respond for Agent1
    plan1 = agent1.plan()
    print(f"Agent1 Plan: {plan1}")
    response1 = agent1.respond(conversation, "Agent2")
    print(f"Agent1: {response1}")

    # Plan and respond for Agent2
    plan2 = agent2.plan()
    print(f"Agent2 Plan: {plan2}")
    response2 = agent2.respond(response1, "Agent1")
    print(f"Agent2: {response2}")

    # Track responses for saving
    responses.append((agent1.name, response1))
    responses.append((agent2.name, response2))

    # Continue conversation
    conversation = response2

    # Reflect every 3 iterations
    if (i + 1) % 3 == 0:
        reflection1 = agent1.reflect()
        print(f"Agent1 Reflection: {reflection1}")
        reflection2 = agent2.reflect()
        print(f"Agent2 Reflection: {reflection2}")
        # Track reflections for saving
        responses.append((agent1.name, reflection1))
        responses.append((agent2.name, reflection2))

# Final agreement prompt
final_prompt = "Based on our discussion, what is our final agreed-upon design for the power plant?"

# Agents finalize the agreement
final_response1 = agent1.finalize_agreement(final_prompt)
print(f"Agent1's Final Agreement: {final_response1}")

final_response2 = agent2.finalize_agreement(final_prompt)
print(f"Agent2's Final Agreement: {final_response2}")

# Track final agreements for saving
responses.append((agent1.name, final_response1))
responses.append((agent2.name, final_response2))

# Display the final design agreement
print("\nFinal Design Agreed Upon:")
print(f"Agent1: {final_response1}")
print(f"Agent2: {final_response2}")

# Save memories to CSV files
save_memory_to_csv('agent1_memory.csv', agent1.memory)
save_memory_to_csv('agent2_memory.csv', agent2.memory)

# Save responses to a CSV file
save_responses_to_csv('conversation_responses.csv', responses)
