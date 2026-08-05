import assets as ast

def pf(delta_t):
	stocks = ast.Asset(0.06, 0.15, 1E08, delta_t)
	bonds = ast.Asset(0.03, 0.05, 3E07, delta_t)
	real_estate = ast.Asset(0.05, 0.10, 5E07, delta_t)
	miscellaneous = ast.Asset(0.045, 0.08, 2E07, delta_t)
	pf = [stocks, bonds, real_estate, miscellaneous]
	corr_matrix = [
		[1.0, 0.1, 0.4, 0.3],
		[0.1, 1.0, 0.2, 0.15],
		[0.4, 0.2, 1.0, 0.35],
		[0.3, 0.15, 0.35, 1.0]
	]
	return pf, corr_matrix