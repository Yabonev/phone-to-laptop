# Claude Code and Agentic Coding Presentation

## I. How people normally used it when ChatGPT became quite well known

### A. The first level - browser and codebase back and forth
- "they just went to ChatGPT and they started talking to it and they explained their problem"
- "if you needed to bring some file context because ChatGPT can't know about your codebase you just copy-pasted a bunch of stuff"
- "You went back and forth between the browser chat and then your codebase"
- "I brainstormed with it, I gave it files as context and then I asked it questions"
  - "brainstormed different architectures for the given feature"
  - "what files to have, how to name them, what to do with them"
  - "what methods to have, which methods belong to each file and so on"
- "After that it creates something, you copy-paste it, you run it, it breaks, you go back and forth to fix it"

### B. The few issues with that
- "it's quite slow like each file that you have you have to paste in the chat"
- "running the project and build errors you also have to manually copy-paste"
- "depending on the feature you might have to go through a lot of files, paste a lot of stuff"
- "But essentially the underlying model and how it works it's quite the same now"

## II. Then Cursor and Windsurf became quite popular

### A. The huge advantage of these tools
- "while ChatGPT and Claude Sonnet and so on didn't have is exactly fixing those issues which is access to the code base"
- "you could then in Cursor select the model you would like to have and either be in Ask mode or in Edit mode"
- "have the AI generate file"

### B. How this works - the second wave
- "it did indexing of your whole code base. It created a vector database of your code"
- "A vector database essentially is just taking in your code base each piece of code in some kind of way separated becomes a number"
- "then you can do... And then the stuff that is similar goes to the same place"
- **TODO:** "expand on the concept of vector database"

### C. The huge win of this was
- "you didn't have to paste context"
- "You just had to somehow provide it like drag and drop whole folders"
- "ask questions about it and so on"
- "Essentially, the difference was that you had the chat but it was locally and it knew more about your code base"
- "it had it indexed so it has access to it"
- "you could do it in a way that does not copy-paste it but rather just references the files"

## III. The next thing that came is this agentic mode

### A. Before that came MCP servers
- "But I think we will come back to them later and their usefulness"
- **TODO:** "speak about what is an MCP server"

### B. With the tools, the main thing that happened
- "it gave the ability to the agents to execute different things"
- "Cursor got this agentic mode. Windsurf got the agentic mode. Copilot got the agentic mode"
- "And then we also have Claude Code, and... 100 different solutions"

### C. Problems with early agentic tools
- "It just did not work well enough"
- "There are a lot of... There is a lot of stuff that goes on in the background. And that takes context"
- "You did not know how much context you have available with Windsurf. Literally there was nothing like it"
- "turns out that it's a lot less than you expect"
- "A lot of the context was reserved to be used internally"
- "In Cursor you have around 120,000 context available from it. Which is like... 40% of it is off limits"
- "And then you have Max Mode. Which is... Just pure... Money... Fire... Throwing money in the fire. The same as Claude Code"

## IV. And then... You get Claude Code

### A. "And that's the next thing"
- "Claude Code is just a lean agentic wrapper on top of the models"
- "you get almost the whole context I would say"
- "it is a CLI version of Cursor"
- "you just have... Access to the tools. And it works quite well"

### B. The main thing that blew my mind - the to-do list
- "One of its core features is that it has the ability to create and follow to-do tasks"
- "when you give it more complex tasks it creates A to-do list and then starts executing based on that to-do list until it exhausts it"
- "This is achieved through prompting. So there is a system prompt"
- "it's called a style in the latest version"
- "gives Claude Code this software development persona and tool calling capabilities"
- "when you're doing a complex task use your to-do right tool to create to-do list and then follow them"
- **TODO:** "find the system prompt and talk about it for a bit"

## V. Brief introduction to agentic coding

### A. These models, they get tools
- "when I say tools, think something like web search, web fetch"
- "search in Google or some other search engine"
- "Fetch the page, understand the content, list current directory"
- "bash tool which enables it to run bash scripts or bash commands"
- "read file, write to file. Grep which is extremely strong"
- "To find references in the content of the files themselves"

### B. What makes them quite interesting - having these tools
- "What would happen if you developed the application normally is that you would basically sit down, start writing the code. Research documentation"
- "Write the code, run the code, get build errors, fix build errors, run the code again"
- "open the UI, test, fix bugs, commit, check console works"
- "write tests, commit and then bam you have some kind of application and feature running"
- "when you want to introduce changes you would look at the codebase, you would see what is already there"
- "add new files, update existing files, refactor, remove files, run again, build again, test again"
- "this is kind of like the non-linear development loop of software"

### C. With tools you can short-circuit this feedback loop
- "the few things that you can do development-wise"
- "Claude Code has the ability to read bash output and have background tasks using running in bash"
- "you would create something, you would have, let's say, Python backend and React frontend and then you would run it"
- "You either run it in a separate console tab, like a separate terminal"
- "when something is wrong. You copy-paste the errors in the chat"
- "you log the errors in a file and then you say to the model, hey, please read the logs"

### D. Background bash tasks and read bash output
- "you get background bash tasks and then a new tool, which is read bash output"
- "gives the ability to the model to run a background task"
- "it kind of closes the feedback loop, it writes the code and then it can run it and then see if it runs successfully"
- "If it runs successfully, it can just stop and tell you it's done"
- "if it doesn't run successfully, it continues to iterate on the build errors until it runs successfully"

## VI. Having access to everything

### A. Example with React frontend and Python backend
- "you can run the React frontend... with the background bash commands"
- "You can run the Python backend with the background bash command"
- "you can add Chrome MCP, which gives you the ability to read console logs"
- "Claude code can read logs, which are related to the build of the code for the React"
- "it can also read the browser, tab logs. related to the runtime"
- "if you encounter some runtime issue you can say hey I encountered a runtime issue please check the console logs with the chrome mcp"
- "it will go and read the logs and you don't have to copy paste stuff"

### B. The loop at this point
- "from the large language model it writes code it can then build it see errors and then it stops when everything is fine"
- "the second step would be you use the application you find some errors"
- "you tell it hey I found this errors check the console it reads them and then fixes it and hopefully it builds again"
- "the few moments where you interact with it is you give it the task that it has to do"
- "the other part is the testing of the application at this point"

### C. For the testing of the application
- "you can use Playwright MCP or the Chrome MCP and give it access to the browser"
- "it can open browser instances, it can take screenshots, it can essentially execute end-to-end tests"
- "Chrome MCP can open a browser tab in your existing browser and reuse all your cookies and everything else"
- "it opens the browser, it uses the features, it takes screenshots to see if everything's working correctly"
- "it checks all the terminals and browser console for any errors"
- "takes again screenshots to ensure everything is correct"

## VII. Even if you set this up... fundamental challenges

### A. "You still... get hit with fundamental challenges"
- "they're autocomplete, basically a glorified autocomplete on steroids that can do a bunch of stuff"
- "it can hallucinate, it can make errors, it goes into this cascade mode"
- "you tell it fix something and just because it spends time on fixing it, it makes errors"
- "if you tell it, hey, fix this issue and it spends like 100,000 tokens on fixing this"
- "It can then take a screenshot and the screenshot is completely wrong and it's obvious to you"
- "it says... yeah. now it's fixed I even took a screenshot to prove it"
- "spending out the context on something is like surest way to ensure hallucinations"

### B. Context and model limitations
- "your success becomes dependent on the on the quality of your prompts"
- "how do you measure quality of prompt"
- "do you provide enough context for the model to do the right thing"
- "did you tell it to research did you tell it to build to use the mcp to test and what to look for"

### C. Model behavior patterns - Anthropic models example
- "one of the few things that they do is they always comment code"
- "the system style tells it to do not write comments until explained explicitly asks it ignores this and it writes comments all the time"
- "it comments every class it comments every property it comments every method it comments in line in the method"
- "you can prompt it to not do it and maybe in five or six messages it does it again"
- "it's really let's say biased and this is probably training data to writing comments"

### D. "it just hallucinates stuff and it says it just you tell it to do something it doesn't do it"
- "it loves to do fallback implementations"
- "it tries to install the model it doesn't succeed because it hits a gated repo"
- "sometimes it says hey there is a gated repo you need to set the hugging face token"
- "it's biased towards completing its tasks and it just goes and creates mocks"
- "it generates some kind of sine or cosine wave and then you you have the whole application and it's like one-shotted and it just doesn't work"

## VIII. Disclaimer about agentic coding

### A. "this is just my best guess I would say"
- "how to make the model not hallucinate that it has achieved something that it has not achieved"
- "to not hit the dreaded you're absolutely right, I fucked up your code base and now you cannot work"
- "if there was a solution about this, then I would say yes"

### B. "if you had a bunch of words split in text files that gave you the ability to write arbitrary feature requests"
- "that would probably be a really hidden knowledge currently"
- "Everyone is trying to remove the effort and time and money it needs to write the code"
- "if you can just prompt something that writes it. Updates it. Ensure that it's working either by tests or it tests itself"
- "that's like the golden goose"
- "it's similar to if you have a working investment strategy, do you really write a book about it or do you just use it to make lots of money?"
- "if someone really got it to work 100% of the time, I don't imagine that they will share it"

### C. Current reality
- "This is not an easy thing to do. It is not a solved problem"
- "It is not at the level of I'm completely... I'm a non-technical person who knows nothing about code"
- "And I have 3 max accounts or whatever. It's not working"
- "whatever you find, everyone is trying to solve this"

## IX. Context engineering - giving as much context as possible

### A. "In order to have the model do better and do whatever you want"
- "giving as much context as possible that is on the topic is the best bet"
- "you don't want to feed it unnecessary information, but you want to feed it a lot of necessary information and that's to the point where you repeat stuff"

### B. Speech to text
- "one of the simplest things you can do is speech to text"
- "just know that it will be strange and people around you will look at you strangely if you're using it"
- "My girlfriend told me that it reminded her of it felt like a real life episode of Black Mirror"
- "you can speak a lot more words then you can type"
- "speaking, and just starting a recording and recording is going forces you to think"
- "when i'm speaking i feel like it's a lot more focusing"
- "during the time i'm speaking i'm realizing things i'm iterating over them and i'm fixing some issues"
- "i repeat the important bits and i say and now this is really important which kind of focuses the model"

### C. Expert definition - being specific about what you mean
- "explaining in depth what you want to achieve"
- "explaining it what you mean by words is also important"
- "when you say uh expert in something what do you mean by expert"
- "when you say be an expert in something you mean something you want something out of it some kind of behavior"
- "extracting that behavior and adding it to the prompt itself is generally more successful"
- **Example:** "expert qa tester"
  - "what you want actually is a model with the system system prompt that forces it or biases it towards writing comprehensive tests"
  - "tests that mock only what is needed but test what it needs to be tested"
  - "it tests the core the main functionality the most important things"
  - "it doesn't test a bunch of nonsense that will break under the um simplest change"

### D. Reflection requirement
- "there is a huge amount of reflection going on when you start using these models"
- "if you really want to prompt for the best response you have to be you have to really ask yourself what you really want"
- "you really have to ask yourself um what are the"
- "you kind of have to also um fitting what you really want and then base it towards being able to bias a large language model towards achieving what you want"
- "being realistic about the things it will do and it will not do"

### E. Rules and their limitations
- "having some kind of rules, let's say. And the rule is always use UV"
- "Never use Python directly, always lint the code, always write tests, do not write comments and so on"
- "those generally get ignored or even when they're not ignored they are kind of hallucinated"

## Leaf Topics for Further Research

- "expand on the concept of vector database"
- "speak about what is an MCP server"
- "find the system prompt and talk about it for a bit"
- Hugging Face token setup and gated repository handling
- Chrome MCP vs Playwright MCP detailed comparison
- Background bash task management strategies
- Context window optimization techniques
- Fallback implementation detection and prevention
- Speech-to-text workflow optimization
- Rule enforcement system effectiveness
- Model bias patterns across different providers
- Cost analysis of Max Mode vs standard context usage