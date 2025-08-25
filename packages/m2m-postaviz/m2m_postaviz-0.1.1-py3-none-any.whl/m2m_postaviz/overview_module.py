import plotly.express as px
import polars as pl
from shiny import module
from shiny import reactive
from shiny import render
from shiny import ui
from shinywidgets import output_widget
from shinywidgets import render_widget
from faicons import icon_svg as icon

import m2m_postaviz.shiny_module as sm
from m2m_postaviz.data_struct import DataStorage


@module.ui
def overview_module_ui(Data: DataStorage):

    factor_list = Data.get_factors()
    factor_list.insert(0, "None")

    metadata_label = Data.get_factors()
    metadata_label.remove("smplID")

    welcome_card = ui.card(ui.output_ui("Starting_message"))

    cpds_reached = ui.card(
        ui.card_header("Numbers of unique metabolites reached by community members, either individually or taking into account interactions across populations.",
            ui.tooltip(
                ui.input_action_button("info_reach_plot", " ", icon=icon("circle-question")),
                    "This plot depicts the number of unique metabolites reached in each sample, either individually by any population (without interactions with others) or collectively taking into account interactions across populations ('Comm_reached'). Please start by selecting a metadata variable. Statistical tests can be applied to compare groups. Check 'Multiple test correction' if appropriate, and select the associated method."),), 


        ui.layout_sidebar(
            ui.sidebar(
                
                ui.input_select("cpd_reach_input", "metadata selection", choices=factor_list),
                ui.input_checkbox("multiple_correction_reach_plot", "Multiple test correction"),
                ui.panel_conditional("input.multiple_correction_reach_plot",
                    ui.input_select("multiple_test_method_reach","Method",
                        ["bonferroni","sidak","holm-sidak","holm","simes-hochberg","hommel","fdr_bh","fdr_by","fdr_tsbh","fdr_tsbky"],
                        selected="bonferroni",)),

                ui.input_task_button("run_reached_cpd","Go"),
                width=300,
                bg="lightgrey"
                ),

            ui.card(output_widget("cpd_reach_plot"), full_screen=True),
            ui.card(ui.output_data_frame("cpd_reach_test_dataframe"),full_screen=True)
        )
    )

    total_production_plot = ui.card(
    ui.card_header("Total production of metabolites in communities, weighted with the relative abundance data of populations if provided.",
                   ui.tooltip(
                        ui.input_action_button("info_tot_plot", " ", icon=icon("circle-question")), "Ovearall reached metabolites, taking into account the relative abundance of populations in each sample. If you have abundance data, you can check the box to use it for the plot. You can also select two metadata variables to label the X axes. Statistical tests can be applied to compare groups. Check 'Multiple test correction' if appropriate, and select the associated method. Data used to construct the dataframe and statistical test results can both be exported to files."),), 
    ui.layout_sidebar(
        ui.sidebar(
            ui.input_select("prod_inputx1", "Metadata variable for X axis", factor_list),
            ui.input_select("prod_inputx2", "Metadata variable for 2nd X axis", factor_list),

            ui.input_checkbox("prod_norm", "Abundance data"),
            ui.input_checkbox("multiple_correction_global_plot", "Multiple test correction"),
            ui.panel_conditional("input.multiple_correction_global_plot",ui.input_select("multiple_test_method_global","Method",
                                                                                                    ["bonferroni","sidak","holm-sidak","holm","simes-hochberg","hommel","fdr_bh","fdr_by","fdr_tsbh","fdr_tsbky"],
                                                                                                    selected="bonferroni",)),

            ui.input_action_button("export_global_production_plot_dataframe_button", "Export plot dataframe"),
            ui.output_text_verbatim("export_global_production_plot_dataframe_txt", True),
            ui.input_action_button("export_global_production_test_button", "Export stats dataframe"),
            ui.output_text_verbatim("export_global_production_test_dataframe", True),
            width=300,
            gap=30,
            bg="lightgrey"
        ),

        ui.card(ui.p(output_widget("total_production_plot")),full_screen=True),

        ui.card(ui.output_data_frame("production_test_dataframe"),full_screen=True)

    ),
    full_screen=True
    )

    pcoa_card = ui.card(
                    ui.card_header("Principal Coordinate Analysis",
                        ui.tooltip(
                            ui.input_action_button("info_reach_plot", " ", icon=icon("circle-question")), "PCoA perfomed on the whole dataset of samples. Select a metadata variable to color the data points. You may hide or select samples using filter provided. Note that it will not recalculate the distance matrix, simply highlight the selected samples.")),
                    ui.layout_sidebar(
                        ui.sidebar(
                            ui.input_select(id="pcoa_color", label="Metadata variable for point coloring.", choices=metadata_label, selected=metadata_label[0]),
                            ui.output_ui("pcoa_ui"),
                            ui.help_text(ui.output_text("display_warning_pcoa")),
                            width=300,
                            gap=30,
                            bg="lightgrey",

                        ),
                    output_widget("pcoa_plot")
                    ),
                    full_screen=True,
                    min_height="600px"
                    )

    custom_pcoa_card = ui.card(
                            ui.card_header("Customized Principal Coordinate Analysis",
                                ui.tooltip(
                                    ui.input_action_button("info_reach_plot", " ", icon=icon("circle-question")), "Customize the PCoA by selecting only samples of interest. Select a metadata variable and select groups of samples by filtering the values of that variable")),  
                            ui.layout_sidebar(
                                ui.sidebar(

                                    ui.input_select(id="custom_pcoa_selection", label="Metadata variable", choices=metadata_label, selected=metadata_label[0]),
                                    ui.output_ui("pcoa_custom_choice"),
                                    ui.input_select(id="pcoa_custom_color", label="Color", choices=metadata_label, selected=metadata_label[0]),
                                    ui.input_checkbox("pcoa_custom_abundance_check", "Use abundance data."),

                                    ui.input_task_button("run_custom_pcoa","Go"),
                                    width=300,
                                    gap=35,
                                    bg="lightgrey"
                                ),
                            output_widget("pcoa_custom_plot"),
                            ),
                            full_screen=True,
                            min_height="600px"
                        )

    global_overview = ui.card(
        ui.layout_column_wrap(

            ui.value_box(
                "Numbers of unique metabolic networks:",
                ui.output_text("unique_total_bin_count"),
                theme="bg-gradient-indigo-purple",
            ),

            ui.value_box(
                "Numbers of samples:",
                ui.output_text("total_samples_count"),
                theme="cyan",
            ),

            ui.value_box(
                "Numbers of unique metabolites reached by samples:",
                ui.output_text("total_unique_cpd"),
                theme="bg-gradient-blue-purple",
            ),

            fill=False,
            ),
            cpds_reached,
            total_production_plot,
    )

    return welcome_card, global_overview, pcoa_card, custom_pcoa_card

@module.server
def overview_module_server(input, output, session, Data: DataStorage):

    @render.ui
    def Starting_message():
        msg = (
            '<div style="white-space: normal;">'
            "Welcome to the <b>M2M Post-Analysis Visualization App</b>!<br>"
            'This app allows you to explore your microbiome models generated by <a href="https://github.com/AuReMe/metage2metabo" target="_blank">Metage2Metabo</a> in various ways.<br>'
            "You can visualize the data globally on this tab, explore the role of several populations in '<i>Taxonomy-based exploration</i>', "
            "explore specific functions in tab '<i>metabolite-based explorations</i>'.<br>"
            "You can also manage your metadata by changing the data types of columns in the '<i>Metadata management</i>' tab.<br>"
            "Please select the appropriate tab to get started or start digging into your data below.<br>"
            'If you have any questions, please refer to the online '
            '<a href="https://metage2metabo-postaviz.readthedocs.io/en/latest/reference/m2m_postaviz.html" target="_blank">documentation</a> '
            'or raise an issue on <a href="https://github.com/AuReMe/metage2metabo-postaviz/tree/main" target="_blank" > GitHub</a>.<br>'
            '</div>'
        )
        return ui.HTML(msg)

    @render.text
    @reactive.event(input.export_global_production_test_button)
    def export_global_production_test_dataframe():

        dataframe_to_save = Data.get_working_dataframe("total_production_test_dataframe")
        if dataframe_to_save is None:

            log = "Unable to find any dataframe to save."

        log = Data.save_dataframe(dataframe_to_save, "producer_test_dataframe")

        return log

    @render.text
    @reactive.event(input.export_global_production_plot_dataframe_button)
    def export_global_production_plot_dataframe_txt():

        dataframe_to_save = Data.get_working_dataframe("total_production_plot_dataframe")
        if dataframe_to_save is None:

            log = "Unable to find any dataframe to save."

        log = Data.save_dataframe(dataframe_to_save, "producer_plot_dataframe")

        return log

    @render_widget
    def total_production_plot():

        fig, df = sm.render_reactive_total_production_plot(Data, input.prod_inputx1(), input.prod_inputx2(), input.prod_norm())

        Data.keep_working_dataframe("total_production_plot_dataframe", df, on_RAM_only=True)

        return fig

    @reactive.effect
    @reactive.event(input.run_reached_cpd, ignore_none=False, ignore_init=True)
    def handle_click_reached_cpd():
        make_cpd_reached_plot(input.cpd_reach_input(), input.multiple_correction_reach_plot(), input.multiple_test_method_reach())

    @ui.bind_task_button(button_id="run_reached_cpd")
    @reactive.extended_task
    async def make_cpd_reached_plot(metadata_column, multiple_correction, correction_method):
        
        return sm.cpd_reached_plot(Data, metadata_column, multiple_correction, correction_method)

    @render.data_frame
    def cpd_reach_test_dataframe():

        return make_cpd_reached_plot.result()[1]
    
    @render_widget
    def cpd_reach_plot():

        return make_cpd_reached_plot.result()[0]

    @render.data_frame
    def production_test_dataframe():

        test_dataframe = sm.global_production_statistical_dataframe(Data, input.prod_inputx1(),
                                                            input.prod_inputx2(),
                                                            input.multiple_correction_global_plot(),
                                                            input.multiple_test_method_global(),
                                                            input.prod_norm())

        Data.keep_working_dataframe("total_production_test_dataframe", test_dataframe, on_RAM_only=True)

        return test_dataframe

    @render.text
    def unique_total_bin_count():
        return Data.get_total_unique_bins_count()

    @render.text
    def total_samples_count():
        return str(Data.get_main_dataframe().shape[0])

    @render.text
    def total_unique_cpd():
        return str(Data.get_main_dataframe().shape[1])

    @render.text
    def display_warning_pcoa():
        return "Warning: this is just for display, Pcoa's dataframe is not recalculated."

    @reactive.effect
    @reactive.event(input.run_custom_pcoa, ignore_none=False)
    def handle_click():
        make_custom_pcoa(input.custom_pcoa_selection(), input.pcoa_custom_choice(), input.pcoa_custom_abundance_check(), input.pcoa_custom_color())

    @ui.bind_task_button(button_id="run_custom_pcoa")
    @reactive.extended_task
    async def make_custom_pcoa(column, choices, abundance, color):

        return sm.make_pcoa(Data, column, choices, abundance, color)

    @render_widget
    def pcoa_custom_plot():
        return make_custom_pcoa.result()

    @render.ui
    @reactive.event(input.custom_pcoa_selection)
    def pcoa_custom_choice():

        df = Data.get_metadata()
        values = df.get_column(input.custom_pcoa_selection())

        if not df.get_column(input.custom_pcoa_selection()).dtype.is_numeric():

            return ui.TagList(
                    ui.card(" ",
                        ui.input_selectize("pcoa_custom_choice", "Get only in column:", values.unique().to_list(),
                                            selected=values.unique().to_list(),
                                            multiple=True,
                                            options={"plugins": ["clear_button"]})
                    ,max_height="400px"
                    ))
        else:

            return ui.TagList(
                        ui.input_slider("pcoa_custom_choice", "Set min/max filter:", min=values.min(), max=values.max(), value=[values.min(),values.max()]),)

    @render_widget
    def pcoa_plot():
        # Get all parameters.
        selected_col = input.pcoa_color()

        df = Data.get_pcoa_dataframe()

        # Check column dtype.
        if df.get_column(selected_col).dtype.is_numeric():

            min_limit = input.pcoa_slider()[0]

            max_limit = input.pcoa_slider()[1]

            df = df.filter((pl.col(selected_col) <= max_limit) & (pl.col(selected_col) >= min_limit))

        else:

            show_only = input.pcoa_selectize()

            df = df.filter(pl.col(selected_col).is_in(show_only))

        fig = px.scatter(df, x="PC1", y="PC2", title="PCoA of reached metabolites in samples (Jaccard distance)", color=selected_col)

        return fig

    @render.ui
    @reactive.event(input.pcoa_color)
    def pcoa_ui():

        df = Data.get_pcoa_dataframe()
        values = df.get_column(input.pcoa_color())

        if not df.get_column(input.pcoa_color()).dtype.is_numeric():

            return ui.TagList(
                    ui.card(" ",
                        ui.input_selectize("pcoa_selectize", "Show only:", values.unique().to_list(),
                                            selected=values.unique().to_list(),
                                            multiple=True,
                                            options={"plugins": ["clear_button"]}),
                        max_height="400px"
                        ))
        else:

            return ui.TagList(
                        ui.input_slider("pcoa_slider", "Set min/max filter:", min=values.min(), max=values.max(), value=[values.min(),values.max()]),)
