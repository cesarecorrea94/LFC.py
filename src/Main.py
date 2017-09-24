#!/usr/bin/env python
#coding: utf-8
'''
Created on 15/06/2017

@author: cesar
'''
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GObject, GLib
from GUI import GUI
from os import sys

def main():
    '''
    Abre o arquivo com a interface usuário, conecta os sinais do usuário (cliques de botões) a rotinas,
    e chama a rotina Gtk.main()
    '''
    
    builder = Gtk.Builder()
    builder.add_from_file("myglade.glade")
    builder.connect_signals({
            "on_window1_destroy": Gtk.main_quit,
            "on_criar_clicked": GUI.on_criar_clicked,
            "on_deletar_clicked": GUI.on_deletar_clicked,
            "on_criarER_clicked": GUI.on_criarER_clicked,
            "on_criarAF_clicked": GUI.on_criarAF_clicked,
            "on_determinizar_clicked": GUI.on_determinizar_clicked,
            "on_minimizar_clicked": GUI.on_minimizar_clicked,
            "on_complemento_clicked": GUI.on_complemento_clicked,
            "on_união_clicked": GUI.on_uniao_clicked,
            "on_intersecção_clicked": GUI.on_interseccao_clicked,
            "on_diferença_clicked": GUI.on_diferenca_clicked,
            })
    builder.get_object('window1').show_all()
    GUI._builder = builder
    Gtk.main()
    pass

if __name__ == '__main__':
    sys.exit(main())
    pass
