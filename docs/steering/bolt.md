Prompt effectively
Tips for writing better prompts

To help you write better prompts, reuse them, and save time while building your favorite projects, we have a new feature called Prompt library. Head over to the Interacting with Bolt section to see how you can fully utilize this feature.
​
Automatically improve your prompt
Bolt has a built-in feature to help you create better prompts:
Write your prompt in the chatbox.
Click Enhance prompt Star icon. Bolt generates a recommended prompt, which you can then edit.
"Gif showing a short prompt being copied into Bolt, the user clicks enhance prompt, and Bolt converts it to a more detailed prompt"
​
Prompting tips
For more detail, a Bolt user has written a great Guide to Bolt.new Prompting.
Some quick tips:
Start with the application architecture, including your choice of tools, frameworks, and so on.
Add individual components and features, one by one.
Add in details in each component with small, specific prompts. Avoid overwhelming the LLM with too many instructions and requirements at once.
Be explicit about what should and shouldn’t change. You can tell Bolt to change or not change specific files. When possible, refer to specific elements, classes, or functions to guide Bolt to the exact place where you want the changes made.
Don’t expect the LLM to have common sense.
​
Guide Bolt’s focus
You’ll get more accurate results if you’re explicit about what Bolt should and shouldn’t change.
​
Limit Bolt to specific files
Right-click the files you want to focus on in the Bolt Code editor.
Select Target file.
​
Exclude specific files or directories
Right-click the files or directories you want to exclude in the Bolt Code editor.
Select Lock file (single file) or Lock all (directory).
​
Focus on a specific code section
Make sure you’re in Code view.
Highlight the code you want to discuss or change.
Click the Ask Bolt button (if the button doesn’t appear immediately, try right-clicking). Bolt links the selection in the prompt box.
Enter your question or request.
​
Focus on a specific UI element
In Preview view, click Inspector Inspector icon.
Click the element you want to focus on. Bolt links the selection in the prompt box.
Enter your question or request.
​
Troubleshooting prompting
Some tips for resolving common issues.
​
Bolt didn’t do everything you asked it to do in your prompt
Break your changes into smaller pieces. Ask the AI to do one thing at a time.
Make a change.
Check if the change works.
Move to the next feature.
​
Bolt forgets what you told it earlier in the same chat
The context window isn’t infinite.
A way to preserve context while keeping the context window small is to get the AI to summarize the conversation so far, then reset the context window. Refer to Reset the AI context window for instructions.
​
Customize the project and system prompts
The project and system prompts are additional messages sent to the AI model, telling it how to behave, and providing additional context. This is useful if you always want the AI to behave a certain way.
Project versus system prompts:
The project prompt is specific to your current project.
The system prompt applies to every project.
Update the prompts:
Open the menu by hovering over the left side of the screen or clicking Open sidebar Open sidebar icon . If you want to update a project prompt, you must be in the project. You can’t update the prompt while Bolt is thinking and the project is building.
Click Settings > Knowledge.
Update the Project Prompt or Global System Prompt.
Click Save prompt. Bolt confirms whether the prompt updated successfully.
Here’s an example, from Bolt’s Vite React starter project:

Copy

Ask AI
For all designs I ask you to make, have them be beautiful, not cookie cutter. Make webpages that are fully featured and worthy for production.

By default, this template supports JSX syntax with Tailwind CSS classes, the shadcn/ui library, React hooks, and Lucide React for icons. Do not install other packages for UI themes, icons, etc unless absolutely necessary or I request them.

Use icons from lucide-react for logos.

Use stock photos from unsplash where appropriate.
​
Tips for the project or system prompts
Include instructions to Bolt to only change relevant code.