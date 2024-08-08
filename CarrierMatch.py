import networkx as nx
import matplotlib.pyplot as plt
import json
import re
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

# Function to load companies from a JSON file
def load_companies(file_path):
    with open(file_path, 'r') as file:
        companies = json.load(file)
    return companies

# Function to create the graph
def create_graph(companies):
    G = nx.Graph()
    for company, attrs in companies.items():
        G.add_node(company, **attrs)
        for connection in attrs.get('connections', []):
            G.add_edge(company, connection)
    return G

# Function to calculate skill match score
def calculate_skill_match(user_skills, company_skills):
    user_skills_set = set(user_skills.lower().split(","))
    company_skills_set = set(company_skills.lower().split(","))
    match_score = len(user_skills_set & company_skills_set) / len(company_skills_set) if company_skills_set else 0
    return 1 - match_score  # higher match_score means lower skill difference

# Tree Node and Binary Search Tree classes
class TreeNode:
    def __init__(self, score, company):
        self.score = score
        self.company = company
        self.left = None
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    def insert(self, score, company):
        if not self.root:
            self.root = TreeNode(score, company)
        else:
            self._insert(self.root, score, company)

    def _insert(self, node, score, company):
        if score < node.score:
            if node.left:
                self._insert(node.left, score, company)
            else:
                node.left = TreeNode(score, company)
        else:
            if node.right:
                self._insert(node.right, score, company)
            else:
                node.right = TreeNode(score, company)

    def in_order_traversal(self, node, result):
        if node:
            self.in_order_traversal(node.left, result)
            result.append((node.score, node.company))
            self.in_order_traversal(node.right, result)

# Define the recommendation function
def recommend_companies(G, user_qualification, user_salary, user_experience, user_skills):
    bst = BinarySearchTree()

    for company, attrs in G.nodes(data=True):
        qualification_score = 0 if user_qualification == attrs['qualification'] else 1
        salary_score = abs(user_salary - attrs['salary'])
        experience_score = abs(user_experience - attrs['experience'])
        skills_score = calculate_skill_match(user_skills, attrs['skills'])

        total_score = qualification_score + salary_score + experience_score + skills_score

        bst.insert(total_score, company)

    result = []
    bst.in_order_traversal(bst.root, result)

    top_3_companies = result[:3]
    return top_3_companies

# Validation functions
def is_valid_email(email):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    return re.match(pattern, email)

def is_valid_phone(phone):
    pattern = r"^\+?[0-9]{10,15}$"
    return re.match(pattern, phone)

def is_non_empty_string(s):
    return bool(s and s.strip())

def is_positive_integer(n):
    return n.isdigit() and int(n) > 0

def is_valid_salary(salary):
    return salary.isdigit() and int(salary) >= 0

# Function to get and validate user input from the form
def get_user_input():
    user_details = {
        "full_name": full_name_var.get(),
        "email": email_var.get(),
        "phone": phone_var.get(),
        "address": address_var.get(),
        "city": city_var.get(),
        "state": state_var.get(),
        "zip_code": zip_code_var.get(),
        "country": country_var.get(),
        "qualification": qualification_var.get(),
        "field_of_study": field_of_sty_var.get(),
        "years_of_experience": years_of_experience_var.get(),
        "expected_salary": expected_salary_var.get(),
        "skills": skills_var.get(),
    }

    if not is_non_empty_string(user_details["full_name"]):
        return "Invalid full name. Please try again."
    if not is_valid_email(user_details["email"]):
        return "Invalid email. Please try again."
    if not is_valid_phone(user_details["phone"]):
        return "Invalid phone number. Please try again."
    if not is_non_empty_string(user_details["address"]):
        return "Invalid address. Please try again."
    if not is_non_empty_string(user_details["city"]):
        return "Invalid city. Please try again."
    if not is_non_empty_string(user_details["state"]):
        return "Invalid state. Please try again."
    if not is_positive_integer(user_details["zip_code"]):
        return "Invalid zip code. Please try again."
    if not is_non_empty_string(user_details["country"]):
        return "Invalid country. Please try again."
    if user_details["qualification"] not in ["Bachelors", "Masters", "PhD"]:
        return "Invalid qualification. Please enter Bachelors, Masters, or PhD."
    if not is_non_empty_string(user_details["field_of_study"]):
        return "Invalid field of study. Please try again."
    if not is_positive_integer(user_details["years_of_experience"]):
        return "Invalid years of experience. Please enter a positive integer."
    if not is_valid_salary(user_details["expected_salary"]):
        return "Invalid expected salary. Please enter a non-negative integer."
    if not is_non_empty_string(user_details["skills"]):
        return "Invalid skills. Please try again."

    return user_details

# Function to visualize the graph
def visualize_graph(G, top_3_companies):
    pos = nx.spring_layout(G, k=0.3)  # k parameter adjusts the distance between nodes
    pos['Chennai'] = (0, 0)  # Centering Chennai

    plt.figure(figsize=(12, 8))

    # Draw nodes with default color
    nx.draw_networkx_nodes(G, pos, node_color='skyblue', node_size=1500, alpha=0.8)

    # Draw the Chennai node separately with a different color and increased size
    nx.draw_networkx_nodes(G, pos, nodelist=['Chennai'], node_color='lightpink', node_size=3000, alpha=0.9)

    # Draw top 3 companies with different colors
    if len(top_3_companies) > 0:
        nx.draw_networkx_nodes(G, pos, nodelist=[top_3_companies[0][1]], node_color='green', node_size=2000, alpha=0.9)
    if len(top_3_companies) > 1:
        nx.draw_networkx_nodes(G, pos, nodelist=[top_3_companies[1][1]], node_color='yellow', node_size=2000, alpha=0.9)
    if len(top_3_companies) > 2:
        nx.draw_networkx_nodes(G, pos, nodelist=[top_3_companies[2][1]], node_color='red', node_size=2000, alpha=0.9)

    # Draw edges with different styles to represent roads
    road_styles = ['solid', 'dashed', 'dotted']
    road_widths = [2, 3, 4]
    for i, (u, v) in enumerate(G.edges()):
        style = road_styles[i % len(road_styles)]
        width = road_widths[i % len(road_widths)]
        nx.draw_networkx_edges(G, pos, edgelist=[(u, v)], style=style, width=width, alpha=0.5, edge_color='grey')

    # Draw labels with different font sizes
    labels = {node: node for node in G.nodes()}
    font_sizes = {node: 16 if node == 'Chennai' else 10 for node in G.nodes()}
    
    for node, (x, y) in pos.items():
        plt.text(x, y, labels[node], fontsize=font_sizes[node], ha='center', va='center')

    plt.title("Company Recommendation System")
    plt.show()

# Callback function for the submit button
def on_submit():
    user_input = get_user_input()
    if isinstance(user_input, dict):
        user_qualification = user_input["qualification"]
        user_salary = int(user_input["expected_salary"])
        user_experience = int(user_input["years_of_experience"])
        user_skills = user_input["skills"]

        top_3_companies = recommend_companies(G, user_qualification, user_salary, user_experience, user_skills)
        if top_3_companies:
            recommended_companies = [company for _, company in top_3_companies]
            messagebox.showinfo("Recommendation", f"Top recommended companies for you:\n1. {recommended_companies[0]}\n2. {recommended_companies[1]}\n3. {recommended_companies[2]}")
            visualize_graph(G, top_3_companies)
        else:
            messagebox.showinfo("Recommendation", "No suitable company found.")
    else:
        messagebox.showerror("Input Error", user_input)

# Load companies data
companies = load_companies('companies.json')

# Create the graph
G = create_graph(companies)

# Create the GUI application
root = tk.Tk()
root.title("CareerMatch")

# Set the background color
root.configure(background='#c8dcf0')

# Create a frame for the form
form_frame = ttk.Frame(root, padding="10", style='My.TFrame')
form_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Style configuration
style = ttk.Style()
style.theme_use('clam')
style.configure('TButton', background='#4CAF50', foreground='white', font=('Helvetica', 12), padding=10)
style.configure('TLabel', background='#f0f0f0', font=('Helvetica', 10))
style.configure('TEntry', font=('Helvetica', 10))
style.configure('My.TFrame', background='#f0f0f0')
style.map('TButton', background=[('active', '#45a049')])

# Create and set variables for form fields
full_name_var = tk.StringVar()
email_var = tk.StringVar()
phone_var = tk.StringVar()
address_var = tk.StringVar()
city_var = tk.StringVar()
state_var = tk.StringVar()
zip_code_var = tk.StringVar()
country_var = tk.StringVar()
qualification_var = tk.StringVar()
field_of_sty_var = tk.StringVar()
years_of_experience_var = tk.StringVar()
expected_salary_var = tk.StringVar()
skills_var = tk.StringVar()

# Create the form fields
fields = [
    ("Full Name", full_name_var),
    ("Email", email_var),
    ("Phone", phone_var),
    ("Address", address_var),
    ("City", city_var),
    ("State", state_var),
    ("Zip Code", zip_code_var),
    ("Country", country_var),
    ("Qualification (Bachelors/Masters/PhD)", qualification_var),
    ("Field of Study", field_of_sty_var),
    ("Years of Experience", years_of_experience_var),
    ("Expected Salary", expected_salary_var),
    ("Skills (comma separated)", skills_var)
]

entry_width = 30

for i, (label, var) in enumerate(fields):
    ttk.Label(form_frame, text=label, style='TLabel').grid(row=i, column=0, padx=5, pady=5, sticky=tk.W)
    ttk.Entry(form_frame, textvariable=var, width=entry_width, style='TEntry').grid(row=i, column=1, padx=5, pady=5, sticky=tk.W)

# Create the submit button
ttk.Button(form_frame, text="Submit", command=on_submit, style='TButton').grid(row=len(fields), column=0, columnspan=2, pady=20)

# Make the form expandable
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)
form_frame.columnconfigure(1, weight=1)

# Run the GUI main loop
root.mainloop()
