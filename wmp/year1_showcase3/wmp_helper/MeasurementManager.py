#!/usr/bin/python
__author__ = 'Pierluigi Gallo'
"""
EU project WISHFUL
"""

import sys
import time
from time import gmtime, strftime
from numpy import *
from datetime import datetime, date, timedelta
import matplotlib
import json
import numpy as np
#from common.upihelper import unix_time_as_tuple, get_now_full_second, dumpFuncName

# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot as plt, os, fnmatch
from matplotlib.backends.backend_pdf import PdfPages

class MeasurementCollector:
    """
    This class defines a collector that takes measurements and parameters from several nodes involved in the
    experiment and takes the most appropriate actions in answer to the collected values. Beware, this have a
    network-wide view, unlike any single node that has a local view.
    """

    def __init__(self, mytestbed, log):
        self.mytestbed = mytestbed
        self.log = log
        self.measurement_types = []

    def column(self, matrix, i):
        return [row[i] for row in matrix]

    def clear_nodes_measurements(self, nodes):
        """ Clear all the measurement stored in WiFiNode object.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        """
        for node in nodes:
            node.last_bunch_measurement = []
        return

    def plot_measurements(self, plot_title, plot_directory):
        #get experiment log
        with open(plot_directory+'/measure.json') as data_file:
            data = json.load(data_file)

        measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH', 'THR']
        #node_list = ["192.168.3.102", "192.168.3.103", "192.168.3.104", "192.168.3.105", "192.168.3.110", "192.168.3.113", "192.168.3.114"]
        node_list = ["192.168.3.103", "192.168.3.104", "192.168.3.105", "192.168.3.110", "192.168.3.113", "192.168.3.114"]
        ip_mask = "192.168.3.1"

        print(data.keys())
        print("%s" % str(sorted(data.keys())))

        node_num = 0
        for node in list(sorted(data.keys())):

                nodeIp=node
                node_num +=1
                x = array(data.get(nodeIp))
                dim = x.shape
                figure_id = 0
                xaxis = []



                if len(dim) > 2:
                        number_type_measurements = dim[2]
                else:
                        number_type_measurements = 1

                if number_type_measurements > 1 :
                        for meas_type_id in range(number_type_measurements):
                                if measurement_types[meas_type_id] == "TSF" :
                                        min_TSF=np.min(x[:,0,meas_type_id])
                                        for ii in range(dim[0]):
                                                for jj in range(dim[1]):
                                                        xaxis.append(x[ii][jj][meas_type_id])

                for meas_type_id in range(number_type_measurements):
                        if not ((measurement_types[meas_type_id] == "TSF") and (number_type_measurements > 1)) :
                                my_dpi=100
                                width=1024
                                height=768

                                yaxis = []
                                figure_id += 1

                                if nodeIp in node_list:

                                        print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")
                                        for ii in range(dim[0]):
                                                for jj in range(dim[1]):
                                                        yaxis.append(x[ii][jj][meas_type_id])

                                        fig=plt.figure(figure_id)
                                        ax = fig.add_subplot(111)
                                        nodeIp_label=nodeIp.replace(ip_mask,"sta")
                                        nodeIp_label = 'sta' + str(node_num) + '(CWOPT)'

                                        ax.plot((xaxis-min_TSF)/1e6,yaxis,label=nodeIp_label);
                                        ax.grid(True)
                                        ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])

                                        #measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH', 'THR']
                                        #[[1065.0, 304423959, 241.0, 25, 3.578125, 318, 1290.0, 874427.0, 1027761.0, 239.0, 2575.0]]

                                        if (measurement_types[meas_type_id] == "FREEZING_NUMBER"):
                                                ax.set_ylim([0, 2000])

                                        if (measurement_types[meas_type_id] == "RX_ACK_RAMATCH"):
                                                ax.set_ylim([0, 400])

                                        if (measurement_types[meas_type_id] == "CW"):
                                                ax.set_ylim([0, 70])

                                        if (measurement_types[meas_type_id] == "IPT"):
                                                ax.set_ylim([0, 25])

                                        if (measurement_types[meas_type_id] == "TX_DATA"):
                                                ax.set_ylim([0, 500])

                                        if (measurement_types[meas_type_id] == "RX_ACK"):
                                                ax.set_ylim([0, 2200])

                                        if (measurement_types[meas_type_id] == "BUSY_TIME"):
                                                ax.set_ylim([0, 1000000])

                                        if (measurement_types[meas_type_id] == "NUM_RX_MATCH"):
                                                ax.set_ylim([0, 2500])

                                        if (measurement_types[meas_type_id] == "THR"):
                                                ax.set_ylim([0, 5000])

                                        x_limit = [7, 60]
                                        #x_limit = [3, 30]
                                        ax.set_xlim(x_limit)

                                        fig.set_size_inches(width/my_dpi,height/my_dpi)
                                        plt.tight_layout()
                                        #legend = ax.legend()
                                        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3, fancybox=True, shadow=True)

                                        #plt.show()
                                        fig_filename="%s/fig_%s.pdf" % (plot_directory, measurement_types[meas_type_id])
                                        ax.set_ylabel(measurement_types[meas_type_id])
                                        ax.set_xlabel('time [s]')
                                        fig.savefig(fig_filename, format='pdf')


    def plot_measurements_mixed(self, plot_title, plot_directory_start_1, plot_directory_start_2, plot_directory):
        #get experiment log
        with open(plot_directory_start_1+'/measure.json') as data_file:
            data_1 = json.load(data_file)

        with open(plot_directory_start_2+'/measure.json') as data_file:
            data_2 = json.load(data_file)

        measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH', 'THR']
        #if nodeIp=="10.8.8.102" or nodeIp=="10.8.8.105" or nodeIp=="10.8.8.107" or nodeIp=="10.8.8.110" or nodeIp=="10.8.8.111" or nodeIp=="10.8.8.112" or nodeIp=="10.8.8.113" or nodeIp=="10.8.8.114" or nodeIp=="10.8.8.5":
        #node_list = ["192.168.3.102", "192.168.3.103", "192.168.3.104", "192.168.3.105", "192.168.3.110", "192.168.3.113", "192.168.3.114"]
        node_list = ["192.168.3.103", "192.168.3.104", "192.168.3.105", "192.168.3.110", "192.168.3.113", "192.168.3.114"]
        ip_mask = "192.168.3.1"

        print("%s" % str(sorted(data_1.keys())))
        print("%s" % str(sorted(data_2.keys())))

        node_num = -3
        min_TSF_1 = 0
        min_TSF_2 = 0
        for node in list(sorted(data_1.keys())):

                nodeIp=node
                node_num += 2

                x_data_1 = array(data_1.get(nodeIp))
                dim_1 = x_data_1.shape

                x_data_2 = array(data_2.get(nodeIp))
                dim_2 = x_data_2.shape

                figure_id = 0
                xaxis_1 = []
                xaxis_2 = []

                if len(dim_1) > 2:
                        number_type_measurements = dim_1[2]
                else:
                        number_type_measurements = 1

                if number_type_measurements > 1 :
                        for meas_type_id in range(number_type_measurements):
                                if measurement_types[meas_type_id] == "TSF" :
                                        min_TSF_1 = np.min(x_data_1[:, 0, meas_type_id])
                                        for ii in range(dim_1[0]):
                                                for jj in range(dim_1[1]):
                                                        xaxis_1.append(x_data_1[ii][jj][meas_type_id])

                                        min_TSF_2 = np.min(x_data_2[:, 0, meas_type_id])
                                        for ii in range(dim_2[0]):
                                                for jj in range(dim_2[1]):
                                                        xaxis_2.append(x_data_2[ii][jj][meas_type_id])



                for meas_type_id in range(number_type_measurements):
                        if not ((measurement_types[meas_type_id] == "TSF") and (number_type_measurements > 1)) :
                                my_dpi=100
                                width=1024
                                height=768


                                figure_id += 1

                                if nodeIp in node_list:

                                        fig=plt.figure(figure_id)
                                        ax = fig.add_subplot(111)
                                        #nodeIp_label=nodeIp.replace(ip_mask,"sta")

                                        print(" node : " + nodeIp + " ( plot --> " + measurement_types[meas_type_id] + " )")
                                        yaxis = []
                                        for ii in range(dim_1[0]):
                                                for jj in range(dim_1[1]):
                                                        yaxis.append(x_data_1[ii][jj][meas_type_id])

                                        if node_num < 5 :
                                            nodeIp_label_1 = 'sta' + str(node_num) + '(CWOPT)'
                                            nodeIp_label_2 = 'sta' + str(node_num+1) + '(CWOPT)'
                                        elif node_num == 5:
                                            nodeIp_label_1 = 'sta' + str(node_num) + '(CWOPT)'
                                            nodeIp_label_2 = 'sta' + str(node_num+1) + '(LEGACY)'
                                        else:
                                            nodeIp_label_1 = 'sta' + str(node_num) + '(LEGACY)'
                                            nodeIp_label_2 = 'sta' + str(node_num+1) + '(LEGACY)'


                                        if (measurement_types[meas_type_id] == "THR"):
                                            yaxis = [x / 2 for x in yaxis]
                                        ax.plot((xaxis_1-min_TSF_1)/1e6, yaxis, label=nodeIp_label_1)

                                        yaxis = []
                                        for ii in range(dim_2[0]):
                                                for jj in range(dim_2[1]):
                                                        yaxis.append(x_data_2[ii][jj][meas_type_id])

                                        if (measurement_types[meas_type_id] == "THR"):
                                            yaxis = [x / 2 for x in yaxis]
                                        ax.plot((xaxis_2-min_TSF_2)/1e6, yaxis, label=nodeIp_label_2)



                                        #measurement_types=['FREEZING_NUMBER', 'TSF', 'RX_ACK_RAMATCH', 'CW', 'IPT', 'TX_DATA', 'RX_ACK', 'BUSY_TIME', 'delta_TSF', 'NUM_RX_MATCH', 'THR']
                                        #[[1065.0, 304423959, 241.0, 25, 3.578125, 318, 1290.0, 874427.0, 1027761.0, 239.0, 2575.0]]

                                        if (measurement_types[meas_type_id] == "FREEZING_NUMBER"):
                                                ax.set_ylim([0, 2000])

                                        if (measurement_types[meas_type_id] == "RX_ACK_RAMATCH"):
                                                ax.set_ylim([0, 400])

                                        if (measurement_types[meas_type_id] == "CW"):
                                                ax.set_ylim([0, 60])

                                        if (measurement_types[meas_type_id] == "IPT"):
                                                ax.set_ylim([0, 25])

                                        if (measurement_types[meas_type_id] == "TX_DATA"):
                                                ax.set_ylim([0, 500])

                                        if (measurement_types[meas_type_id] == "RX_ACK"):
                                                ax.set_ylim([0, 2200])

                                        if (measurement_types[meas_type_id] == "BUSY_TIME"):
                                                ax.set_ylim([0, 1000000])

                                        if (measurement_types[meas_type_id] == "NUM_RX_MATCH"):
                                                ax.set_ylim([0, 2500])

                                        if (measurement_types[meas_type_id] == "THR"):
                                                ax.set_ylim([0, 3000])

                                        x_limit = [7, 60]
                                        #x_limit = [3, 30]
                                        ax.set_xlim(x_limit)
                                        #ax.set_xlim([0, (np.max(xaxis)-np.min(xaxis))/1e6])
                                        ax.grid(True)

                                        fig.set_size_inches(width/my_dpi,height/my_dpi)
                                        plt.tight_layout()
                                        #legend = ax.legend()
                                        legend = ax.legend(loc='upper center', bbox_to_anchor=(0.5, 1), ncol=3, fancybox=True, shadow=True)


                                        #plt.show()
                                        fig_filename="%s/fig_%s.pdf" % (plot_directory, measurement_types[meas_type_id])

                                        if not(measurement_types[meas_type_id] == "THR"):
                                            ax.set_ylabel(measurement_types[meas_type_id])
                                        else:
                                            ax.set_ylabel('Thr [kbps]')
                                        ax.set_xlabel('time [s]')
                                        fig.savefig(fig_filename, format='pdf')



    def plot_last_measurements(self, nodes, measurement_types, plot_title, plot_directory):
        """ Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        :param measurement_types: list of measurements name.
        :param plot_title: the title to write on graphic plot.
        """

        self.log.info("*********** Plot measurement *************")
        enable_plot = 0

        out_measure = {}

        for node in nodes:
            self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))

        #save experiments log
        with open(plot_directory+'/measure.json', 'w') as outfile:
            for node in nodes:
                out_measure.update({node.wlan_ipAddress : node.last_bunch_measurement});

            json.dump(out_measure, outfile)

        if enable_plot:
            self.plot_measurements(plot_directory, plot_title)


    def generate_measurement_report(self, nodes, filename="experiment_report.pdf"):
        """ Uses matplotlib library to plot all the measurements stored in WiFiNode object.
            Uses PdfPages to create a pdf with graphical plot.
            The measurements are stored in the last_bunch_measurement attribute of WiFiNode class.

        :param nodes: list of WiFiNode.
        :param filename: file name of the pdf report.
        """
        if self.measurement_types == None:
            self.log.info("no measurement to include in the report. Report has not been created!")
            return
        for node in nodes:
            self.log.info("node : %s - measurements : %s" % (str(node), node.last_bunch_measurement))
            if node.last_bunch_measurement == []:
                self.log.info("no measurement to include in the report. Report has not been created!")
                return

        with PdfPages(filename) as pdf:
            cover = plt.figure(0)
            textstring = "WiSHFUL experiment report \n" \
                         "Experiment finished at \n " \
                         " " + strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

            cover.text(0.5, 0.5, textstring,
                       fontweight='bold',
                       verticalalignment='center',
                       horizontalalignment='center',
                       color='green', fontsize=15)
            pdf.savefig(cover)

            for node in nodes:
                x = array(node.last_bunch_measurement)
                dim = x.shape
                figure_id = 1
                xaxis = []

                for meas_type_id in range(dim[2]):
                    if self.measurement_types[meas_type_id] == "TSF" :
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                xaxis.append(x[ii][jj][meas_type_id])

                for meas_type_id in range(dim[2]):
                    if self.measurement_types[meas_type_id] != "TSF" :
                        yaxis = []
                        figure_id += 1
                        for ii in range(dim[0]):
                            for jj in range(dim[1]):
                                yaxis.append(x[ii][jj][meas_type_id])
                        plt.figure(figure_id)
                        plt.plot(xaxis, yaxis)
                        plt.title(self.measurement_types[meas_type_id])
                        plt.grid()
                        plt.draw()
                        time.sleep(1)
                        pdf.savefig(cover)
            plt.show()

        return
