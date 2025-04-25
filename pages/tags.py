import streamlit as st
from db import load_tag_rules, load_extracted_tags, add_tag_rule, delete_tag_rule, delete_extracted_tag
from tagger import auto_tag_reviews


def show_tags(app_id='cashgiraffe.app'):
    st.header("Tags")
    st.markdown("Manage tags and tag rules for the selected app.")

    # Load tag rules and extracted tags
    tag_rules = load_tag_rules(app_id)
    extracted_tags = load_extracted_tags(app_id)

    # Add new tag rule
    st.subheader("Add New Tag Rule")
    with st.form(key='add_tag_form'):
        tag_name = st.text_input("Tag Name")
        keywords = st.text_input("Keywords (comma-separated)")
        submit_button = st.form_submit_button(label='Add Tag Rule')
        if submit_button:
            if tag_name and keywords:
                try:
                    keywords_list = [kw.strip() for kw in keywords.split(',')]
                    add_tag_rule(app_id, tag_name, keywords_list)
                    st.success(f"Added tag rule: {tag_name}")
                    st.experimental_rerun()
                except Exception as e:
                    st.error(f"Error adding tag rule: {e}")
            else:
                st.error("Please provide both tag name and keywords.")

    # Display current tag rules
    st.subheader("Current Tag Rules")
    if tag_rules:
        for tag, keywords in tag_rules.items():
            with st.expander(f"Tag: {tag}"):
                st.write(f"**Keywords:** {', '.join(keywords)}")
                if st.button(f"Delete {tag}", key=f"delete_rule_{tag}"):
                    try:
                        delete_tag_rule(app_id, tag)
                        st.success(f"Deleted tag rule: {tag}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error deleting tag rule: {e}")
    else:
        st.write("No tag rules defined.")

    # Display extracted tags with pagination
    st.subheader("Extracted Tags")
    if 'tags_page' not in st.session_state:
        st.session_state['tags_page'] = 0

    if extracted_tags:
        total_tags = len(extracted_tags)
        items_per_page = st.sidebar.selectbox("Items per page", [10, 20, 50, 100], key="tags_items_per_page", index=1)
        total_pages = (total_tags + items_per_page - 1) // items_per_page

        if total_pages > 1:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Previous", key="tags_previous_button", disabled=(st.session_state['tags_page'] == 0)):
                    st.session_state['tags_page'] -= 1
                    st.experimental_rerun()
            with col2:
                if st.button("Next", key="tags_next_button", disabled=(st.session_state['tags_page'] == total_pages - 1)):
                    st.session_state['tags_page'] += 1
                    st.experimental_rerun()

        start_index = st.session_state['tags_page'] * items_per_page
        end_index = start_index + items_per_page
        paginated_tags = extracted_tags[start_index:end_index]

        for tag in paginated_tags:
            with st.expander(f"Tag: {tag}"):
                if st.button(f"Delete {tag}", key=f"delete_extracted_{tag}"):
                    try:
                        delete_extracted_tag(app_id, tag)
                        st.success(f"Deleted extracted tag: {tag}")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Error deleting extracted tag: {e}")

    else:
        st.write("No extracted tags available.")

    # Auto-tag reviews
    st.subheader("Auto-Tag Reviews")
    if st.button("Run Auto-Tagging"):
        try:
            auto_tag_reviews(app_id)
            st.success("Auto-tagging completed successfully!")
        except Exception as e:
            st.error(f"Error during auto-tagging: {e}")
