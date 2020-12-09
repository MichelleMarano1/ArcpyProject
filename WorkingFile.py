# Authors of code include Tayler Nichol, Aaron Jutzi, Michelle Marano, Kimberly Hansen
# Last Modified 2020-12-08
# Tayler Nichol create script in model builder, coded overall structure of code ( clusters, for loops, arcpy), 
# Aaron coded overall structure of code(dictionary, XYTableToPoint, arcpy)
# Michelle built coded that was not used like a dictionary, design overall interface, wrote the try excpects and inputs, inputed top of code comments
# Kimberly Hansen Created host repository
# Program Purpose
# This program will allow the user to evaluate forest fire activity in the region chosen. 
# You Will upload a CSV file, the program will output cluster information to about hotspots
# and are behavior by classifying the different cluster type i.e clumped, dispersed, random. 
# Brief Structure 
# Code is in a try excpet, we harded the files and used relative paths, created a dictiory for names, 
# User is asked to select a province or territory, a shapefile is then created for said province or territory containing firepoint data,
# boundary shapefile is then used to clip the firepoints to the selected province or territory.
# User inputs miniuim amount of features for each cluster and the search distance
# The clusters are assigend an ID expect noise point assinged -1, noise is not part of clumped cluster goes into dispered to be analysis
# The clumped cluster and dispered shapefiles are made and downloaded for the into the output folder
# Assumptions
# You want to anaylize 2019, you have the folder download with all the relative paths
# Assume that they know what they are obsvering so they know the values
# Aussume the user knows what to do with the outputed information
# Limitations
# You have the folder download with all the relative paths conncted to a program like VSC
# You need a GIS program to see the outputs
# The code will not work with ArcPro open
# Know Problems
# You can only analyze yearly data, you cannot analyze data within a couple of months
# Input
# the inputs is harded coded which is the modis csv, the user will then input province or territory, 
# miniuim amount of features for each cluster and the search distance 
# Outputs
# Cluster data, Dispersed data and a shapefile contating cliped data to users chosen province or territory
# References 
# https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
# https://pro.arcgis.com/en/pro-app/arcpy/classes/env.htm
# https://pro.arcgis.com/en/pro-app/tool-reference/data-management/xy-table-to-point.htm
# https://pro.arcgis.com/en/pro-app/tool-reference/spatial-statistics/densitybasedclustering.htm
# https://pro.arcgis.com/en/pro-app/tool-reference/analysis/clip.htm
# https://pro.arcgis.com/en/pro-app/tool-reference/analysis/select.htm
# Generated by ArcGIS ModelBuilder and altered 

import arcpy, csv

try: 
    # To allow overwriting the outputs change the overwrite option to true.
    arcpy.env.overwriteOutput = True

    # Hard Coded CSV document 
    firePointsTable = "modis_2019_Canada.csv"

    # converting the csv modis file into a point shapefile 
    arcpy.management.XYTableToPoint(firePointsTable, "output\canadafirepoints.shp", 
    "longitude", "latitude","","")   

    # assigning the fire point shapefile to a variable 
    points = "output\canadafirepoints.shp"

    # Canada census tract province and territory boundary shapefile 
    census_tracts = "lpr_000b16a_e\lpr_000b16a_e.shp"

    # Below is a dictionary holding province name values. 
    # The first value of each key represents the values as exactly written in the PRNAME field in the 
    # census tracts file. The second value of each key is the abbrevation of those names which will 
    # be used for file names during the arcpy geoprocessing below.
    provinces_territories = {1:('Newfoundland and Labrador / Terre-Neuve-et-Labrador', 'NL'), 
    2:("Prince Edward Island / Île-du-Prince-Édouard", "PE"),
    3:("Nova Scotia / Nouvelle-Écosse", "NS"), 4:("New Brunswick / Nouveau-Brunswick", "NB"), 
    5:("Quebec / Québec","QC") , 6:("Ontario", "ON"), 7:("Manitoba", "MB"), 8:("Saskatchewan", "SK"),
    9:("Alberta", "AB"), 10:("British Columbia / Colombie-Britannique", "BC"),
    11:("Yukon", "YT"), 12:("Northwest Territories / Territoires du Nord-Ouest", "NT"), 13:("Nunavut", "NU")}

    print()
    print("************************************************************************")
    print()
    # printing the above dictionary for the user to see
    print(provinces_territories)
    print()
    print("************************************************************************")
    print()
    # creating an empty list to hold inputted province names (from dictionary)
    study_area = []
    # creating an empty list to hold inputted province name abbreviations (from dictionary)
    abbr = []

    # while loop that lets the user input as many provinces/territories they want to analyze
    while True: 
        provTer = float(input("Please enter the number corresponding to the province/territory you want to analyze: "))
        study_area.append(provinces_territories[provTer][0]) # Province name from dictionary is appended to study_area
        abbr.append(provinces_territories[provTer][1]) # Province abbreviation is appended to abbr

        print() # User has option to enter more provinces for analysis
        end = input("Do you want to enter another province/territory to analyze (Y/N)? ")
        print()
        if end.upper() == 'N' :
            break
    print()
    print("************************************************************************")
    print()
    print(study_area)
    
    
    # source for looping two lists simultaneously: https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
    # this loop iterates through each inputted province/territory name and abbreviation
    for region, ab in zip(study_area, abbr): # a shapefile of each inputted province/territory is created
        arcpy.Select_analysis(census_tracts, "output\{}ound{}.shp".format("b", ab),
        "PRNAME = '{}'".format(region)) # each output will have its province/territory abbrevation at the end  
        
    
    # each previous clipped province/territory is then used to clip the fire points
    for ab in abbr:
        arcpy.Clip_analysis(points, "output\{}ound{}.shp".format("b", ab),
        "output\clipped_points_{}.shp".format(ab))
    # each output will have its province/territory abbrevation at the end

    # user is asked to input the min amount of features to clipped for each analysis
    minFeatures1 = float(input("Please enter the minimum amount of features for the clumped cluster analysis: "))
    print()
    minFeatures2 = float(input("Please enter the minimum amount of features for the dispersed cluster analysis: "))
    print()
    print("************************************************************************")
    print()
    srcDistance1 = input("Please enter the kilometer search distance for identifying clumped clusters: ") + " Kilometers"
    print()
    srcDistance2 = input("Please enter the kilometer search distance for identifying dispersed clusters (must be larger than first search distance): ") + " Kilometers"

    # Clumped cluster
    # For loop iterates for each inputted province's/territory's clipped fire points
    for ab in abbr:
        print("Creating a clumped cluster shapefile for", ab)
        arcpy.stats.DensityBasedClustering("output\clipped_points_{}.shp".format(ab), 
        "output\Clumped_Cluster_{}.shp".format(ab), 
        "OPTICS", minFeatures1, srcDistance1, "") 

    # Dispersed cluster
    # For loop iterates for each input province/territory clipped fire points

    for ab in abbr: 
        arcpy.Select_analysis("output\Clumped_Cluster_{}.shp".format(ab),"output\Dispersed_Input_{}.shp".format(ab), '"CLUSTER_ID" = -1')

    for ab in abbr:
        print("Creating a dispersed cluster shapefile for: ", ab)
        arcpy.stats.DensityBasedClustering("output\Dispersed_Input_{}.shp".format(ab), 
        "output\Dispersed_Cluster_{}.shp".format(ab),
        "OPTICS", minFeatures2, srcDistance2, "")

    for ab in abbr: 
        arcpy.Select_analysis("output\Dispersed_Cluster_{}.shp".format(ab),"output\Random_Points{}.shp".format(ab),'"CLUSTER_ID" = -1')

    # Michelle Marano
    print()
    print("************************************************************************")
    print()
    print("A shapefile with all your clustered are downloaded into the output folder.")
    print()


# Michelle Marano
except arcpy.ExecuteError:
    print(arcpy.GetMessages(2))  
except Exception:
    e = sys.exc_info()[1]
    print(e.args[0])
    arcpy.AddError(e.args[0])
except:
    print("An Error has occurred")
