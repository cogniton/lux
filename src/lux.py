"""
Lexicon of Uncertain Color Standards
Written by XXXXXXXXXXXXXXXXXXXXXXX

This is a demo script for the LUX release.  
There is an accompanying CSV file.  This script opens it and offers basic functionality
"""

from scipy.stats import gamma as gam_dist
from math import sin, cos, atan2, pi
import xml.etree.ElementTree as ET
class LUX:
    def __init__(self, filename):
        """
        Input: full path filename to lux.csv
        Function: Parse lux.csv and make available several probability functions:
            1) predict(datum): predicts most likely label; return [label,probability]
            2) posterior_likelihood(datum,label): Returns P(datum|label)
            3) full_posterior(datum): returns all labels ordered by decreasing posterior likelihood
        """
        tree = ET.parse(filename)
        root = tree.getroot()

        self.all = {child.get("name"):color_label(child) for child in root}
        
        
    def full_posterior(self, datum):
        probabilities = [[dist.name,dist(datum)] for dist in self.all.values()]
        total = sum([x[1] for x in probabilities])
        return sorted([[name,prob/total] for name,prob in probabilities], key=lambda x:x[1], reverse=True)
        #return sorted([[name,prob] for name,prob in probabilities], key=lambda x:x[1], reverse=True)
        
        
    def predict(self, datum):
        #NOTE: This returns the unnormalized posterior likelihood 
        probabilities = [[dist.name,dist(datum)] for dist in self.all.values()]
        sorted_probabilities = sorted(probabilities, key=lambda x: x[1], reverse=True)
        return sorted_probabilities[0]
    
    def posterior_likelihood(self, datum, label):
        probabilities = [dist(datum) for dist in self.all.values()]
        if label not in self.all.keys(): raise OutOfVocabularyException("Label '%s' was not in the lexicon" % label)
        return self.all[label](datum)/sum(probabilities)
    
    def get_params(self, label):
        return [x.params for x in self.all[label].dim_models]
    
    def get_adj(self, label):
        return self.all[label].dim_models[0].adjust
    
    def get_avail(self,label):
        return self.all[label].availability
    
class color_label:
    def __init__(self,label_node):
        """
        The all-dimension model for each color label
        """
        name = label_node.get("name"); availability = float(label_node.get("availability")); hue_adjust = eval(label_node.get("hue_adjust"))
        
        self.name = name; self.availability = availability
        self.dim_models = [single_dim(child) for child in label_node]
        self.dim_models[0].adjust = hue_adjust

    def __str__(self):
        return self.name
    
    def __repr__(self):
        return self.name
    
    def __call__(self, *args):
        return self.phi(args[0])*self.availability
    
    def phi(self,x):
        return self.dim_models[0].phi(x[0])*self.dim_models[1].phi(x[1])*self.dim_models[2].phi(x[2]) 

class single_dim:
    """
    The single dimension for each color label
    """
    def __init__(self, dim_node):
        def get_node(name):
            for child in dim_node:
                if child.tag==name:
                    return child
        paramdict = {child.tag:child for child in dim_node}
        paramnames =["mulower","shapelower","scalelower","muupper","shapeupper","scaleupper"]
        self.params = [float(paramdict[paramname].get("value")) for paramname in paramnames]
        self.stdevs = [float(paramdict[paramname].get("stdev")) for paramname in paramnames]
        mu1,sh1,sc1,mu2,sh2,sc2 = self.params
        left_gamma=gam_dist(sh1,scale=sc1); lbounds=left_gamma.interval(0.99)
        right_gamma=gam_dist(sh2,scale=sc2); rbounds=right_gamma.interval(0.99)
        self.region = lambda x: (2 if x>mu2 else 1) if x>=mu1 else 0
        self.f= [lambda x: left_gamma.sf(abs(x-mu1)),
                 lambda x: 1,
                 lambda x: right_gamma.sf(abs(x-mu2))]
        self.adjust=False
    
    def phi(self, x):
        if self.adjust: x = atan2(sin(x*pi/180),cos(x*pi/180))*180/pi
        return self.f[self.region(x)](x)

class OutOfVocabularyException(Exception):
    pass
