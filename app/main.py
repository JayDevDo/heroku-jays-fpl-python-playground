#!/usr/bin/env python3
# pyFPL
# main.py

""" python modules """
import	sys
import	time

""" own modules """
import app.static.scripts.rounds	as mod_rnd
import app.static.scripts.fixtures 	as mod_fxt
import app.static.scripts.clubs 	as mod_clb
import app.static.scripts.elements 	as mod_plyr
import app.static.scripts.managers	as mod_mng
import app.static.scripts.teams		as mod_tms
import app.static.scripts.getData	as mod_data
import app.static.scripts.leagues 	as mod_lgs
import app.static.scripts.fdl 		as mod_fdl

from flask import Flask, render_template, url_for, request, redirect

"""		######## variables ######## 	"""
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

app = Flask(__name__)


# HTTP Error 503: Service Unavailable

#################################################
#                Main vars						#
#################################################
global myTeamId
global fplData
global posArr
global lgManagerIds

mod_data.getStatic("r")
myTeamId =	993831
posArr =	["POS","GKP","DEF","MID","FWD"]
fplData =	[
				{ "id":"rounds"		, "data": mod_rnd.getRnds() 		},			#0
				{ "id":"fixtures" 	, "data": mod_fxt.getFxtrs("r") 	},			#1
				{ "id":"clubs"		, "data": mod_clb.getClubs("l") 	},			#2
				{ "id":"players"	, "data": mod_plyr.getElmnts("l") 	},			#3
				{ "id":"ownteam"	, "data": [] },									#4
				{ "id":"oppteam"	, "data": [] },									#5
				{ "id":"LgCls"		, "data": mod_mng.getManagerLeagues(myTeamId,0)},#6
				{ "id":"LgH2h"		, "data": mod_mng.getManagerLeagues(myTeamId,1)},#7
				{ "id":"CrrntFxtrs" , "data": [] },									#8
				{ "id":"lgManIds"	, "data": mod_mng.getManIdsFromLeague(1,436866)},#9
				{ "id":"oppId"		, "data": 2045927 },							#10
				{ "id":"refresh"	, "data": 60 },									#11
				{ "id": "selLg" 	, "data": { "id":436866, "nm":"League 436866"}}	#12
			]

fplData[10]["data"] =	578444
lgManagerIds 		=	fplData[9]["data"]
oppId 				=	fplData[10]["data"]
refr_interval 		=	fplData[11]["data"]

def updFPLdata(idx):
	mod_data.fplDataTS[idx] = float(time.time())

def changeMyTmId(newTmId):
	global myTeamId
	myTeamId = newTmId

def fplDataCounter():
	if fplData :
		cntr = 0
		for d in fplData:
			# print("counting fplData[", str(cntr), "]" )
			if  isinstance( d["data"] , dict ):
				# print("fplData[", str(cntr),"]["data"] is <dict>, count = ", doListCount( d["data"] ) )
				fplData[cntr]["count"] =  doListCount( d["data"] )
			elif isinstance( d["data"] , list ):
				# print("fplData[", str(cntr),"]["data"] is <list>, count = ", doListCount( d["data"] ) )
				fplData[cntr]["count"] =  doListCount( d["data"] )
			else:
				# print("fplData[", str(cntr),"]["data"] is ", type( d["data"] ) )
				fplData[cntr]["count"] =  d["data"]

			cntr += 1
	else:
		print("no fplData !")

def doListCount(dict):
	cntr = 0
	for d in dict:
		cntr +=1
		
	return cntr


def doMyUpdate():
	# print( "doMyUpdate: current myTeamId", str( myTeamId ) )
	myTeam =  mod_tms.getTeam("l", 4, myTeamId  )
	fplData[4]["data"].clear
	fplData[4]["data"] = myTeam

	fplData[6]["data"].clear
	fplData[6]["data"] = mod_mng.getManagerLeagues(myTeamId,0)
	for lg in fplData[6]['data']:
		lg["lgCount"] = mod_lgs.guessLeagueCount(0, int(lg["id"]) ) 

	fplData[7]["data"].clear
	fplData[7]["data"] = mod_mng.getManagerLeagues(myTeamId,1)
	for lg in fplData[7]['data']:
		lg["lgCount"] = mod_lgs.guessLeagueCount(1, int(lg["id"]) ) 



def doOppUpdate():
	global oppId
	oppTeam = mod_tms.getTeam("l", 5, fplData[10]["data"] )
	fplData[5]["data"].clear
	fplData[5]["data"] = oppTeam


def urlError(error_msg):
	print(error_msg)


@app.route("/")
@app.route("/home")
@app.route("/index")
def home():
	fplDataCounter()
	return render_template( 'home.html', fpl=fplData ) 

@app.route('/info', methods=['GET','POST'])
def info():
	global fplData
	fplData[8]["data"] = mod_fxt.getLiveFxtrData()
	doMyUpdate()
	doOppUpdate()
	fplDataCounter()
	return render_template( '01INFO/info.html', fpl=fplData )

@app.route('/fdl', methods=['GET','POST'])
def fdl():
	return render_template( '02FDL/pyFDL.html', fdl=mod_fdl.loadFDLData() ) 


@app.route('/compare', methods=['GET','POST'])
def compare():
	global fplData
	fplData[8]["data"] = mod_fxt.getLiveFxtrData()
	doMyUpdate()
	doOppUpdate()
	return ( render_template( '03LEAGUES/leagues.html', fpl=fplData ) )

@app.route('/opponent/<int:manId>', methods=['GET','POST'])
def opponent(manId):
	global fplData
	global oppId
	fplData[10]["data"] = manId
	oppId = manId
	fplData[8]["data"] = mod_fxt.getLiveFxtrData()
	doMyUpdate()
	doOppUpdate()
	return ( render_template( '03LEAGUES/manSelect/tmCompare/tmCompare.html', fpl=fplData ) )


@app.route('/leagueType/<int:lgTp>', methods=['GET','POST'])
def leaguetype(lgTp):
	global fplData
	fplData[6+lgTp]['data'] = mod_mng.getManagerLeagues(myTeamId,lgTp)

	for lg in fplData[6+lgTp]['data']:
		lg["lgCount"] = mod_lgs.guessLeagueCount(lgTp, int(lg["id"]) ) 

	fplDataCounter()
	return ( render_template( 'loading.html' ))

@app.route('/league/<int:lgTp>/<int:lgId>', methods=['GET','POST'])
def lgTeamAcc(lgTp, lgId):
	global fplData
	fplData[9]["data"]	=	mod_mng.getManIdsFromLeague( lgTp, lgId)
	fplData[12]["data"] = { "id": lgId, "nm": mod_mng.getLgNm(lgId) } 
	return ( render_template( '/03LEAGUES/leagues.html', fpl=fplData ))


@app.route('/explain/teamId.html', methods=['GET','POST'])
def expl_tm_id():
	return render_template( '/04EXPLAIN/teamId.html')


@app.route('/teamId',methods = ['POST'])
def teamId():
	if request.method == 'POST':
		newTmId = request.form['newTmId']
		changeMyTmId(newTmId)
		return redirect(url_for('compare'))


@app.template_filter()
def numberFormat(value):
    return format(int(value), ',d')

###############################################
#                Run app                      #
###############################################
# nav.init_app(app)
if __name__ == '__main__':
	app.run(debug=False)