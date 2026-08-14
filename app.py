response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=st.session_state.messages
    )
    
    # Extract the assistant's reply
    assistant_response = response.choices[0].message.content
    
    # Append and display the response
    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
    with st.chat_message("assistant"):
        st.markdown(assistant_response)
