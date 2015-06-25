__author__ = 'bwolfson'

#some data struct that holds all the files

files = []

class FileForDetonation(object):
    def __init__(self, filename, original_sample_size, sample, timebox, detonation_results):
        self.filename = filename,
        self.original_sample_size = original_sample_size,
        self.sample = sample,
        self.timebox = timebox,
        self.detonation_results = detonation_results


class DetonationResults(object):
    def __init__(self, status, eta_to_analysis, eta_to_complete, analysis_complete, analysis_results = []):
        self.status = status,
        self.eta_to_analysis = eta_to_analysis,
        self.eta_to_complete = eta_to_complete,
        self.analysis_complete = analysis_complete,
        self.analysis_results = analysis_results


class AnalysisResults(object):
    def __init__(self, score, analysis_successful, error_description, analysis_summary):
        self.score = score,
        self.analysis_successful = analysis_successful,
        self.error_description = error_description,
        self.analysis_summary = analysis_summary