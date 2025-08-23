---
tags: [gradio-custom-component, SideBar]
title: gradio_bottombar
short_description: A Bottom bar for Gradio Interface
colorFrom: blue
colorTo: yellow
sdk: gradio
pinned: false
app_file: space.py
---

# `gradio_bottombar`
<a href="https://pypi.org/project/gradio_bottombar/" target="_blank"><img alt="PyPI - Version" src="https://img.shields.io/pypi/v/gradio_bottombar"></a>  

A Bottom bar for Gradio Interface

## Installation

```bash
pip install gradio_bottombar
```

## Usage

```python
# demo/app.py

import gradio as gr
import time
from gradio_bottombar import BottomBar

def chat_response(message, history):    
    history = history or ""
    history += f"You: {message}\n"
    time.sleep(1) # Simulate thinking
    history += f"Bot: Thanks for the message! You said: '{message}'\n"
    return history, ""

def update_label(value):
    return f"Current temperature is: {value}"

with gr.Blocks(theme=gr.themes.Ocean(), title="Full Layout Demo") as demo:
    gr.Markdown(
        """
        # Full Layout Demo: BottomBar with Sidebars
        This demo shows the `BottomBar` with `bring_to_front=True`. Notice how it now renders
        **on top of** the sidebars when they overlap.
        """
    )
       
    with BottomBar(open=False, height=180, bring_to_front=True, rounded_borders=True) as bottom_bar:
        with gr.Row():
            message_box = gr.Textbox(
                show_label=False,
                placeholder="Type your message here...",
                elem_id="message-input",
                scale=7
            )
            send_button = gr.Button("Send", variant="primary", scale=1)
        with gr.Row():
            gr.Button("Upload File")
            gr.Button("Record Audio")
            gr.ClearButton([message_box])

    with gr.Row(equal_height=True):
        with gr.Sidebar(position="left"):
            gr.Markdown("### ⚙️ Settings")
            model_temp = gr.Slider(0, 1, value=0.7, label="Model Temperature")
            temp_label = gr.Markdown(update_label(0.7))
            gr.CheckboxGroup(
                ["Enable History", "Use Profanity Filter", "Stream Response"],
                label="Chat Options",
                value=["Enable History", "Stream Response"]
            )

        with gr.Column(scale=3):
            gr.Markdown("### 🤖 Chat Interface")
            chatbot_display = gr.Textbox(
                label="Chat History",
                lines=25,
                interactive=False
            )

        with gr.Sidebar(position="right"):
            gr.Markdown("### ℹ️ Information")
            gr.Radio(
                ["GPT-4", "Claude 3", "Llama 3"],
                label="Current Model",
                value="Claude 3"
            )
            gr.Dropdown(
                ["English", "Spanish", "Portuguese"],
                label="Language",
                value="Portuguese"
            )
    
    send_button.click(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )
    message_box.submit(
        fn=chat_response,
        inputs=[message_box, chatbot_display],
        outputs=[chatbot_display, message_box]
    )
    model_temp.change(
        fn=update_label,
        inputs=model_temp,
        outputs=temp_label
    )

if __name__ == "__main__":
    demo.launch()
```

## `BottomBar`

### Initialization

<table>
<thead>
<tr>
<th align="left">name</th>
<th align="left" style="width: 25%;">type</th>
<th align="left">default</th>
<th align="left">description</th>
</tr>
</thead>
<tbody>
<tr>
<td align="left"><code>label</code></td>
<td align="left" style="width: 25%;">

```python
str | gradio.i18n.I18nData | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">name of the bottom bar. Not displayed to the user.</td>
</tr>

<tr>
<td align="left"><code>open</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">if True, bottom bar is open by default.</td>
</tr>

<tr>
<td align="left"><code>visible</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, the component will be hidden.</td>
</tr>

<tr>
<td align="left"><code>elem_id</code></td>
<td align="left" style="width: 25%;">

```python
str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string that is assigned as the id of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>elem_classes</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">An optional string or list of strings that are assigned as the class of this component in the HTML DOM. Can be used for targeting CSS styles.</td>
</tr>

<tr>
<td align="left"><code>render</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>True</code></td>
<td align="left">If False, this layout will not be rendered in the Blocks context. Should be used if the intention is to assign event listeners now but render the component later.</td>
</tr>

<tr>
<td align="left"><code>height</code></td>
<td align="left" style="width: 25%;">

```python
int | str
```

</td>
<td align="left"><code>320</code></td>
<td align="left">The height of the bottom bar, specified in pixels if a number is passed, or in CSS units if a string is passed.</td>
</tr>

<tr>
<td align="left"><code>width</code></td>
<td align="left" style="width: 25%;">

```python
int | str
```

</td>
<td align="left"><code>"100%"</code></td>
<td align="left">The width of the bottom bar, specified in pixels if a number is passed, or in CSS units (like "80%") if a string is passed. The bar will be horizontally centered.</td>
</tr>

<tr>
<td align="left"><code>bring_to_front</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">If True, the BottomBar will be rendered on top of all other elements with a higher z-index. Defaults to False.</td>
</tr>

<tr>
<td align="left"><code>rounded_borders</code></td>
<td align="left" style="width: 25%;">

```python
bool
```

</td>
<td align="left"><code>False</code></td>
<td align="left">None</td>
</tr>

<tr>
<td align="left"><code>key</code></td>
<td align="left" style="width: 25%;">

```python
int | str | tuple[int | str, Ellipsis] | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">in a gr.render, Components with the same key across re-renders are treated as the same component, not a new component. Properties set in 'preserved_by_key' are not reset across a re-render.</td>
</tr>

<tr>
<td align="left"><code>preserved_by_key</code></td>
<td align="left" style="width: 25%;">

```python
list[str] | str | None
```

</td>
<td align="left"><code>None</code></td>
<td align="left">A list of parameters from this component's constructor. Inside a gr.render() function, if a component is re-rendered with the same key, these (and only these) parameters will be preserved in the UI (if they have been changed by the user or an event listener) instead of re-rendered based on the values provided during constructor.</td>
</tr>
</tbody></table>


### Events

| name | description |
|:-----|:------------|
| `expand` | This listener is triggered when the BottomBar is expanded. |
| `collapse` | This listener is triggered when the BottomBar is collapsed. |



