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

from streamlit.logger import get_logger
import datetime
import time

# import backend.database
# import backend.automatedquery
# import pages.projectedfedrates


LOGGER = get_logger(__name__)


def run():
    st.set_page_config(
        page_title="Quantitative tools",
        page_icon="👋",
    )

    st.write("# Welcome to Quantitative tools!")
    
    st.markdown('This website is made with the python package Streamlit.\n')
    st.markdown('Select a tools from the sidebar (Correlation calculator or Projected FED rates), the code is available on my <a href="https://github.com/MaximilienA/quantitative-tools" target="_blank">Github repository</a>', unsafe_allow_html=True)


    # ===== TESTING AUTOMATED FIREBASE QUERY ===== 
    # start_automatedquery = st.button("Start/stop automated Firebase query")
        

if __name__ == "__main__":
    run()