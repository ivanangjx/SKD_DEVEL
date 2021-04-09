# Import yaml
import argparse
import yaml
import json
import os
import subprocess
import shutil
import fileinput
from datetime import datetime
import sys

# Utils
import OPPTLogAnalyser




class SafeTrajGenerator:
	"""
	Class use to generate safe trajectories of the pedestrian
	"""
	def __init__(self, config_file_path, goal_areas_index, module_output_dir, timestamp):
		""" 
		Constructor for the Safe Traj Generator Module.
		Each Trajectory generator is identified by a timestamp that is used as a
		prefix in the output files of this module.
		"""

		# Initial settings
		self.timestamp = timestamp
		self.config_path = config_file_path
		self.goal_areas_index = goal_areas_index
		self.module_output_dir = module_output_dir

		# Load configurations
		gen_configs = self.get_skd_configurations()
		# Assert configurations exists
		assert (gen_configs["safe_traj_gen_configs"] != None), "No Safe Traj Gen Configs"
		configs = gen_configs["safe_traj_gen_configs"]
		
		# Assign extra configurations and set output dirs
		try:
			# Set extra configs
			self.goal_area = configs["goal_areas"][self.goal_areas_index]
			self.goal_margins = configs["goal_margins"]
			self.num_samples = configs["samples_per_goal"]
			self.initial_state = configs["initial_state"]
			self.log_post_fix = self.timestamp + "_safe_traj_gen_g_%d_%d" % (self.goal_area[0], self.goal_area[1])			
		
		except Exception as e:
			print("Error in configs")


		# Set output dirs
		self.oppt_logs_dir = self.module_output_dir + "/oppt_logs" + "/%s/goal_%d_%d" % (self.timestamp, self.goal_area[0], self.goal_area[1])
		self.oppt_experiment_cfgs = self.module_output_dir + "/oppt_experiment_cfgs" + "/%s/goal_%d_%d" % (self.timestamp, self.goal_area[0], self.goal_area[1])
		self.safe_trajectories_db = self.module_output_dir + "/safe_trajectories_db" + "/%s/goal_%d_%d" % (self.timestamp, self.goal_area[0], self.goal_area[1])
		self.safe_traj_validator_outdir = self.module_output_dir + "/safe_traj_validator_outdir" "/%s/goal_%d_%d" % (self.timestamp, self.goal_area[0], self.goal_area[1])
		self.safe_trajs_file_name = self.safe_trajectories_db + "/safe_traj_gen_g_%d_%d.json" % (self.goal_area[0], self.goal_area[1])

		# Create module output_dirs
		assert (self.create_module_output_dirs()), "Error creating directores"

		
	def create_module_output_dirs(self):
		""" 
		Creates the corresponding output directories for the SafeTrajGenerator Module
		"""
		# Create ouput dir if not existent
		try:
			# Create Safe Traj Experiment Attempt Logfiles
			os.makedirs(self.oppt_logs_dir)
			# Create DB dir for successful safe crossings in the Safe Traj Experiment attempts
			os.makedirs(self.oppt_experiment_cfgs)
			# Create an oppt_experiment cfg files to record the config files used for each set of experiments
			os.makedirs(self.safe_trajectories_db)
		# Throw exception
		except OSError as error:
			return False

		return True


	def get_skd_configurations(self):
	    """
	    Loads the yaml configuration file for the assessment of a vehicle. The function returns a
	    dictionary with the corresponding configuration fields
	    and values for the assessment.
	    """
	    with open(self.config_path) as config_file:
	        configurations = yaml.full_load(config_file)
	        print(configurations)
	        return configurations


	def run_safe_traj_generator(self, planner_executable_path):
		"""
		Executes the first part of the SKD process by loading
		specific assessment configurations, and executing the experiments.
		"""
		# Create a custom cfg for the safe trajectory scenario to be attempted
		skd_python_dir = os.getcwd()
		
		planner_config = self.gen_safe_traj_oppt_cfg()
		print(planner_config)
		# Need to change the std out and sterr of this 
		result = subprocess.run([planner_executable_path, "--cfg", planner_config], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		# Validate and ouput sucessful save trajs
		safe_traj_validator = SafeTrajValidator(self.get_oppt_log_filepath(), self.safe_traj_validator_outdir)

		# Safe successful safe_trajs
		safe_traj_validator.save_successful_safe_trajs(self.safe_trajs_file_name)

		print("=============================== SAFE TRAJS GENERATED ============================================")



	def get_oppt_log_filename(self):
		return "log_ABT_Pedestrian_" + self.log_post_fix + ".log"

	def get_oppt_log_filepath(self):
		return self.oppt_logs_dir + "/" + self.get_oppt_log_filename()


	def get_safe_traj_filepath(self):
		return self.safe_trajs_file_name


	def gen_safe_traj_oppt_cfg(self):
		""" 
		Generates a new ".cfg" with assessment options set to
		file_options according to the desired goal area, goal margins, and initial state parameters"""

		# Copy from a template cfg file and change the appropiate lines with 'sed'
		skd_python_dir = os.getcwd()
		planner_config_path = skd_python_dir + "/../skd_oppt/cfg/SKDBasicController/SafeTrajGen.cfg"

		# Destination of the new custom safeTrajGen
		assessment_configs_path = self.oppt_experiment_cfgs + "/SafeTrajGen_Goal_%d_%d.cfg" % (self.goal_area[0], self.goal_area[1]) 
		cfg_dst = shutil.copyfile(planner_config_path, assessment_configs_path)

		# Replace contents of file
		self.sed_file(cfg_dst, "logPath =.*", "logPath = %s" % (self.oppt_logs_dir))
		# Replace post fix to file name
		self.sed_file(cfg_dst, "logFilePostfix =.*", "logFilePostfix = %s" % (self.log_post_fix))
		# Replace number of samples 
		self.sed_file(cfg_dst, "nRuns =.*", "nRuns = %d" % (self.num_samples))
		# Set experiments to start from a deterministicc point by setting same lower and upper bound of initil belief dist
		self.sed_file(cfg_dst, "lowerBound =.*", "lowerBound = %s" % (self.list_to_str(self.initial_state)))
		self.sed_file(cfg_dst, "upperBound =.*", "upperBound = %s" % (self.list_to_str(self.initial_state)))
		
		# Replace goal area
		self.sed_file(cfg_dst, "safetyGoalArea =.*", "safetyGoalArea = %s" % (self.list_to_str(self.goal_area)))
		# Replace goal margins
		self.sed_file(cfg_dst, "goalMargins =.*", "goalMargins = %s" % (self.list_to_str(self.goal_margins)))

		return cfg_dst

	def sed_file(self, filepath, old_txt, new_txt):
		subprocess.call(["sed -i 's@%s@%s @' %s" % (old_txt, new_txt, filepath)], shell = True)

	def list_to_str(self, list_var):
		result = "["
		for val in list_var:
			result = result + " %s" % (val)
		result = result + " ]"
		return result



class SafeTrajValidator:
	""" 
	Class to examine the log files describing experiments generated by SafeTrajGenerator
	"""
	def __init__(self, logfile, outputdir):
		self.logfile = logfile
		self.outdir = outputdir
		# Analyser used to examine a log from the associated oppt planner
		self.log_analyser = OPPTLogAnalyser.OPPTLogAnalyser(self.outdir, self.logfile)


	def save_successful_safe_trajs(self, dst_filepath):
		""" 
		Saves all the successful trajectories into a json_file, where
		each trajectory is pair with an index as a key.
		"""
		self.log_analyser.split_runs()
		safe_trajs = self.log_analyser.get_successful_ped_trajectories()

		# Safe trajectories
		safe_trajs_dict = {}
		for safe_traj_index in range(len(safe_trajs)):
			safe_trajs_dict[str(safe_traj_index)] = safe_trajs[safe_traj_index]

		with open(dst_filepath, 'w') as outfile:
			json.dump(safe_trajs_dict, outfile)


def main():
	""" Entry point for assesment """
	argparser = argparse.ArgumentParser(
	description= "Adversary Safe Trajectory Generator")

	argparser.add_argument(
		'-cfg', '--config',
		metavar='configFile',
		type=str,
		help='path to configuration file for SKD Assessment')

	argparser.add_argument(
		'-o', '--outdir',
		metavar='SafeTrajGenModuleOutpuDir',
		type=str,
		help='Parent to output directory of the module')


	# Parse arguments
	args = argparser.parse_args()
	config_path = args.config
	module_outdir = args.outdir

	print(config_path)
	print(module_outdir)

	# Create timestamp
	timestamp = datetime.now().strftime("%m-%d-%H-%M")
	
	# Create a SafeTrajGenerator
	safe_traj_gen = SafeTrajGenerator(config_path, 0, module_outdir, timestamp)
	safe_traj_gen.run_safe_traj_generator()


if __name__ == '__main__':
	main()

