# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
import firebase_admin
from streamlit.logger import get_logger
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import auth

cred = credentials.Certificate('quantitativetoolsdatabase-90b51ea9a1ca.json')
firebase_admin.initialize_app(cred, {"databaseURL" : "https://quantitativetoolsdatabase-default-rtdb.europe-west1.firebasedatabase.app/"})

ref = db.reference("/")

LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Quantitative tools",
        page_icon="👋",
    )

    st.write("# Welcome to Quantitative tools!")
    st.write(ref.get()) 

    st.markdown(
        """
        Streamlit is an open-source app framework built specifically for
        Machine Learning and Data Science projects.
        **👈 Select a demo from the sidebar** to see some examples
        of what Streamlit can do!
    """
    )


if __name__ == "__main__":
    run()
