from flask import Flask, render_template, request, render_template_string, jsonify
from airium import Airium
import argparse
import os

from inspection_utils.dataset_review import dataset_review
from inspection_utils.inspector import inspector



common_css =     '''

                    body {
                        font-family: "Roboto", sans-serif;
                        display: flex;
                        flex-direction: column;
                        justify-content: center;
                        align-items: center;
                        margin: 0;
                        padding: 0 10%;
                        background-color: #ffffff;
                    }
                    
                    .terminal-output {
                        background-color: #2C2C2C;  
                        color: #2298dc; 
                        overflow-y: auto;
                        height: 300px;
                        padding: 10px 20px;
                        margin-bottom: 20px;
                        border-radius: 5px;
                        font-family: monospace;
                        box-shadow: 0px 0px 5px 0px rgba(0, 0, 0, 0.2);
                        width: calc(100% - 40px); 
                    }

                    .terminal-topbar {
                        height: 30px;  
                        background-color: #808080;  
                        position: relative;  
                        width: calc(100% - 40px); 
                    }

                    .terminal-output p {
                        white-space: pre-wrap;  
                    }

                    .terminal-buttons {
                        position: absolute;
                        top: 10px;
                        left: 10px;
                    }



                    .terminal-buttons {
                        position: absolute;
                        top: 7px;  
                        left: 10px;
                    }

                    .terminal-button {
                        display: inline-block;
                        width: 12px;
                        height: 12px;
                        margin-right: 5px;
                        border-radius: 50%;
                    }

                    .terminal-button.close {
                        background: #FF5F57;
                    }

                    .terminal-button.minimize {
                        background: #FFBD2E;
                    }

                    .terminal-button.maximize {
                        background: #27C93F;
                    }

                    .row {
                        display: flex;
                        # flex-wrap: wrap;
                        flex-direction: row;
                        justify-content: space-evenly;
                        width: 100%; 
                    }
                    .row-wide {
                        display: flex;
                        flex-wrap: nowrap;  
                        flex-direction: row;
                        justify-content: center;  
                        width: 100%; 
                    }
                    
                    # form {
                    #     width: 100%;
                    #     max-width: 100%;
                    # }

                    .column {
                        flex: 1 0 35%;  
                        padding: 15px;
                        max-width: 35%;
                        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                        border-radius: 5px;
                        background-color: #ffffff;
                        margin: 2%;
                    }
                    .column-wide {
                        flex: 2 0 65%; 
                        padding: 15px;
                        max-width: 100%; 
                        box-shadow: 0 4px 8px 0 rgba(0, 0, 0, 0.2);
                        border-radius: 5px;
                        background-color: #ffffff;
                        margin: 0 0 2% 0;
                    }

                    
                    .column img {
                        max-width: 100%;
                        height: auto;
                    }

                    .img-container {
                        flex: 100%; 
                        max-width: 80%;  
                    }


                    button, input[type='submit'] {
                        background: linear-gradient(to right, #2298dc, #7a64a7);
                        border: none;
                        border-radius: 25px;
                        color: #fff;
                        padding: 15px 30px;
                        text-align: center;
                        text-decoration: none;
                        display: inline-block;
                        font-size: 20px;
                        margin: 4px 2px;
                        cursor: pointer;
                        transition: 0.3s;
                    }
                    }
                    input[type='text'] {
                        width: 100%;
                        padding: 12px 20px;
                        margin: 8px 0;
                        display: inline-block;
                        border: 1px solid #ccc;
                        border-radius: 4px;
                        box-sizing: border-box;
                        color: grey;
                    }
                    [type="checkbox"]:not(:checked), [type="checkbox"]:checked {
                        position: static;
                        opacity: 1;
                        pointer-events: auto;
                    }
                    label, input[type="checkbox"] {
                        display: inline-block;
                    }
                    input[type="checkbox"] {
                        height: 20px;
                        width: 20px;
                        cursor: pointer;
                    }
                    label {
                        display: block;
                        margin-top: 20px;
                        font-weight: bold;
                        font-size: 18px;
                    }
                    h1 {
                        font-family: Arial, sans-serif; 
                        text-align: center;
                        color: #fff;
                        font-size: 2.5em;
                        margin: 20px;
                    }
                    h2 {
                        font-family: Arial, sans-serif; 
                        text-align: center;
                        color: #2298dc;
                        font-size: 2em;
                        margin: 20px;
                    }
                    
                    .header {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        width: 100%;
                        padding: 20px;
                        box-sizing: border-box;
                        background-color: #2298dc; 

                    }

                    .header-text {
                        margin-left: 20px;
                    }

                    .header-text h1 {
                        font-family: Arial, sans-serif;
                        margin: 0;
                        font-size: 2em;
                        color: #2298dc;
                    }

                    .header-text h3 {
                        font-family: Arial, sans-serif; 
                        margin: 0;
                        font-size: 1.2em;
                        color: #7a64a7;
                    }
                    
                    .slogan {
                        font-style: italic;
                        text-align: center;
                        margin: 10px;
                        font-size: 1.5em;
                        color: #ffffff;
                    }
                    
                    .logo {
                        height: 50px;
                    }
                    .container {
                        max-width: 90%;
                        margin: auto;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        padding: 20px;
                        background-color: #ffffff;
                        border-radius: 5px;
                        box-shadow: 0 0 10px rgba(0,0,0,0.1);

                    }
                    .container h2 {
                        font-size: 1.5em;
                        color: #2298dc;
                    }
                    label {
                        display: block;
                        margin-top: 20px;
                        font-weight: bold;
                        color: black
                    }
                    label div {
                        font-weight: bold;
                    }
                    table.dataframe {
                        font-family: Arial, sans-serif;
                        border-collapse: collapse;
                        width: 100%;
                        font-size: 0.75em;  
                        box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                        margin: 0;  
                        padding: 0;  
                        overflow-wrap: break-word;  
                        word-wrap: break-word;  
                        overflow: auto;  
                    }

                    table.dataframe thead tr {
                        background-color: #2298dc;
                        color: #ffffff;
                        text-align: left;
                    }
                    table.dataframe th,
                    table.dataframe td {
                        padding: 5px;  /* reduce padding */
                    }
                    table.dataframe tbody tr {
                        border-bottom: 1px solid #dddddd;
                    }
                    table.dataframe tbody tr:nth-of-type(even) {
                        background-color: #f3f3f3;
                    }
                    table.dataframe tbody tr:last-of-type {
                        border-bottom: 2px solid #2298dc;
                    }
                '''

#note - the passes parameter is a list of passes for showing on the UI what would technically work.
def get_index_html(ip_address, num_samples, center_frequency, sample_rate, gain, channel, protocol, use_case, testbed, transmitters, project_name, sdr,passes):
    a = Airium()
    global common_css

    a('<!DOCTYPE html>')
    with a.html():
        with a.head():
            a.link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css')
            with a.style():
                a(common_css)
                
        with a.body():
            
                    with a.div(klass='header'):
                        a.h1(_t='Capture recording from software defined radio')
                    with a.div(klass='slogan'):
                        a.img(src="{{ url_for('static', filename='logo.png') }}", alt="Logo", style="width:460px;height:100px;")
                        a.em('Identifying things in spectrum with AI.')
                    with a.form(method='POST', action='/'):
                        with a.div(klass='row-wide'):
                            with a.div(klass='column-wide'):
                                a.h2(_t='Capture Settings')

                                with a.label():
                                    a('IP Address:')
                                a.input(type='text', id='ip_address', name='ip_address', value=ip_address, _t='')
                                a.br()

                                with a.label():
                                    a('Number of Samples:')
                                a.input(type='text', id='num_samples', name='num_samples', value=str(num_samples), _t='')
                                a.br()

                                with a.label():
                                    a('Center Frequency:')
                                a.input(type='text', id='center_frequency', name='center_frequency', value=str(center_frequency), _t='')
                                a.br()

                                with a.label():
                                    a('Sample Rate:')
                                a.input(type='text', id='sample_rate', name='sample_rate', value=str(sample_rate), _t='')
                                a.br()

                                with a.label():
                                    a('Gain:')
                                a.input(type='text', id='gain', name='gain', value=str(gain), _t='')
                                a.br()

                                with a.label():
                                    a('Channel:')
                                a.input(type='text', id='channel', name='channel', value=str(channel), _t='')
                                a.br()

                            with a.div(klass='column-wide'):
                                a.h2(_t='Metadata')

                                with a.label():
                                    a('Protocol:')
                                a.input(type='text', id='protocol', name='protocol', value=protocol, _t='')
                                a.br()

                                with a.label():
                                    a('Use Case:')
                                a.input(type='text', id='use_case', name='use_case', value=use_case, _t='')
                                a.br()

                                with a.label():
                                    a('Testbed:')
                                a.input(type='text', id='testbed', name='testbed', value=testbed, _t='')
                                a.br()

                                with a.label():
                                    a('Transmitters:')
                                a.input(type='text', id='transmitters', name='transmitters', value=transmitters, _t='')
                                a.br()

                                with a.label():
                                    a('Project Name:')
                                a.input(type='text', id='project_name', name='project_name', value=project_name, _t='')
                                a.br()

                                with a.label():
                                    a(f'SDR - Options: {passes}:')
                                a.input(type='text', id='sdr', name='sdr', value=sdr, _t='')
                                a.br()

                        a.input(type='submit', value='Submit')

    return str(a)

def get_curate(recordingsummary):
    global common_css

    a = Airium()
    a('<!DOCTYPE html>')
    with a.html(lang='en'):
        with a.head():
            a.meta(name='viewport', content='width=device-width, initial-scale=1')
            a.title(_t="Dataset Curation")
            a.link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css')  
            with a.style():  
                a(common_css)

    with a.body():
        with a.div(klass='header'):
            a.h1(_t="Dataset Curation")
            # a.img(src='https://www.qoherent.ai/wp-content/uploads/2021/10/part-logo-colour-e1633139269793.png', klass='logo')

        with a.div(klass='row'):
            with a.div(klass='column'):
                a.h2(_t='Recording summary')
                with a.div(id="signal-table"):
                    with a.table(_class="dataframe"):
                        with a.tbody():
                            for column in recordingsummary.columns:
                                with a.tr():
                                    a.th(_t=column)  # Column name goes in the table header
                                    a.td(_t=str(recordingsummary[column].values[0]))  # First row value goes in the table data

            with a.div(klass='column'):
                with a.form(id='folder2dataset', method='post', action='/folder2dataset'):
                    a.h2(_t='Dataset Configuration:')
                    with a.b():
                        a('Example Length:')
                    a.input(type='text', id='example_length', name='example_length', value="512", _t='')
                    a.br()
                    with a.b():
                        a('Primary Label:')
                    a.input(type='text', id='class_1', name='class_1', value="protocol", _t='')
                    a.br()
                    with a.b():
                        a('Second Label:')
                    a.input(type='text', id='class_2', name='class_2', value="use_case", _t='')
                    a.br()
                    with a.b():
                        a('Filename:')
                    a.input(type='text', id='dataset_name', name='dataset_name', value="collision.dat", _t='')
                    a.br()

                    a.input(type='hidden', name='action', value='draft')
                    a.button( onclick="submitForm(['process_files'])", _t='Prepare draft dataset', type="submit")

        with a.form(method='POST', action='/reset'):
            a.button( _t='Clear all and reset', type="submit")

    return str(a)

def generate_draft_html(review_args,curate_args,action, terminal_output):
    a = Airium()
    
    df, m_table, m_table_w_totals, n_table_avg,  stats_table = dataset_review(review_args)


    a('<!DOCTYPE html>')
    with a.html():
        with a.head():
            a.meta(name='viewport', content='width=device-width, initial-scale=1')
            a.link(rel='stylesheet', href='https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css')  
            # a.img(src='https://www.qoherent.ai/wp-content/uploads/2021/10/part-logo-colour-e1633139269793.png', klass='logo')

            a.title(_t='Draft Dataset')

            with a.style():  
                a(common_css)

            with a.script(type="text/javascript"):
                a("""
                    window.onload = function() {
                        document.getElementById("downloadButton").addEventListener("click", function() {
                            var datasetFile = document.getElementById('datasetFile').value;
                            window.open('/download?dataset_file=' + encodeURIComponent(datasetFile), '_blank');
                        });
                    }
                """)

        with a.body():
            with a.div(klass='header', style='padding-left: 20px; padding-right: 20px;'):
                a.h1(_t='Results of Dataset Curation:')
                # with a.div(id='output'):
                #     a('{% for line in output_lines %}')
                #     with a.p():
                #         a('{{ line }}')
                #     a('{% endfor %}')

            with a.div(klass='row'):  #top row
                with a.div(klass='col s12 m4 column'):
                    with a.h2():
                        a('Number of examples per unique pair')
                    with a.div(id="m_table"):
                        with a.table(_class="dataframe"):
                            with a.thead():
                                with a.tr():
                                    a.th(_t="Key")
                                    a.th(_t=str(m_table.name))  
                            with a.tbody():
                                for index, row in m_table.items():  
                                    with a.tr():
                                        a.td(_t=str(index))  
                                        a.td(_t=str(row)) 

                with a.div(klass='col s12 m4 column'):
                    with a.h2():
                        a('Number of examples per label')
                    with a.div(id="m_table_w_totals"):
                        with a.table(_class="dataframe"):
                            with a.thead():
                                with a.tr():
                                    a.th(_t="Index")
                                    for column in m_table_w_totals.columns:
                                        a.th(_t=column)
                            with a.tbody():
                                for index, row in m_table_w_totals.iterrows():
                                    with a.tr():
                                        a.td(_t=str(index))
                                        for item in row:
                                            a.td(_t=str(item))

                with a.div(klass='col s12 m4 column'):
                    with a.h2():
                        a('Vector lengths per label')
                    with a.div(id="n_table_avg"):
                        with a.table(_class="dataframe"):
                            with a.thead():
                                with a.tr():
                                    for column in n_table_avg.columns:
                                        a.th(_t=column)
                            with a.tbody():
                                for index, row in n_table_avg.iterrows():
                                    with a.tr():
                                        a.td(_t=str(index))
                                        for item in row:
                                            a.td(_t=str(item))


            with a.div(klass='row'):  #bottom row
                with a.div(klass='col s12 m6 column'):
                    with a.h2():
                        a('Dataset Statistics')
                    with a.div(id="stats_table"):
                        with a.table(_class="dataframe"):
                            with a.thead():
                                with a.tr():
                                    a.th(_t="Index")
                                    for column in stats_table.columns:
                                        a.th(_t=column)
                            with a.tbody():
                                for index, row in stats_table.iterrows():
                                    with a.tr():
                                        a.td(_t=str(index))
                                        for item in row:
                                            a.td(_t=str(item))

                if action == "draft":
                    with a.div(klass='col s12 m6 column'):
                        with a.form(id='folder2dataset', method='post', action='/folder2dataset'):
                            a.h2(_t='Dataset configuration:')
                            with a.b():
                                a('Subsample examples to a fixed maximum:')
                            a.input(type='text', id='class_1', name='homogenize', value="", _t='')
                            a.br()
                            with a.b():
                                a('Fill gaps with augmentations:')
                            a.input(type='text', id='class_2', name='augment', value="", _t='')
                            a.br()
                            with a.b():
                                a('Drop Classes:')
                            for i, key in enumerate(m_table.index):
                                label = '_'.join(key)
                                with a.div():
                                    a.label(_t=f'{key}', for_=f'drop_{i}')
                                    a.input(type='checkbox', id=f'drop_{i}', name='drop_classes', value=label)
                                a.br()

                            a.input(type='hidden', name='example_length', value=curate_args.example_length)
                            a.input(type='hidden', name='dataset_name', value=curate_args.target_dataset_file)
                            a.input(type='hidden', name='class_1', value=curate_args.keys[0])
                            a.input(type='hidden', name='class_2', value=curate_args.keys[1])
                            a.input(type='hidden', name='action', value='final')
                            a.button( onclick="submitForm(['process_files'])", _t='  Prepare Final  ', type="submit")

                        absolute_file_path = os.path.join(os.getcwd(), curate_args.target_dataset_file)
                        with a.button(id="downloadButton", type="button",_t="Download Draft"):
                            pass
                        a.input(type='hidden', id='datasetFile', value=absolute_file_path)            

                else:
                    print("call the image from dataset review")
                    img = inspector(df,save=True)
                    df=None

                    with a.div(klass='col s12 m4 column img-container'):
                        absolute_file_path = os.path.join(os.getcwd(), curate_args.target_dataset_file)
                        with a.button(id="downloadButton", type="button",_t="Download Dataset"):
                            pass
                        a.input(type='hidden', id='datasetFile', value=absolute_file_path)
                        with a.h2():
                            a('Dataset Image')
                        with a.div(id="ds_img"):
                            a.img(src=f"./static/{img}", alt="Dataset Image")


        
        with a.div(klass='terminal-output'):
            with a.div(klass='terminal-topbar'):  
                with a.div(klass='terminal-buttons'):
                    a.div(klass='terminal-button close')
                    a.div(klass='terminal-button minimize')
                    a.div(klass='terminal-button maximize')
            
            a.pre(_t=terminal_output)  

        with a.form(method='POST', action='/reset'):
            a.button( _t='Clear all and reset', type="submit")
    # Close the HTML document
    a.close_all_elements()
    
    # Return the generated HTML content
    return str(a)