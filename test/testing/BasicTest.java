package testing;

import java.io.File;
import java.io.IOException;

import org.apache.commons.io.FileUtils;

public class BasicTest {

	private static final String OUTPUT_DIR = "tmp";
	private static final String EXPECTED_DIR = "expected";
	private static final String PARAM_DIR = "parameters";

	private final String workingDir;
	private final String script;

	public String getWorkingDir() {
		return workingDir;
	}

	public String getScript() {
		return script;
	}

	public String getOutputDir() {
		return outputDir;
	}

	public String getParamsDir() {
		return paramsDir;
	}

	public String getExpectedDir() {
		return expectedDir;
	}

	private final String outputDir;
	private final String paramsDir;
	private final String expectedDir;

	public BasicTest(final String workingDir, final String script) {
		this.workingDir = workingDir;
		this.script = script;
		this.outputDir = workingDir + File.separatorChar + OUTPUT_DIR;
		this.paramsDir = workingDir + File.separatorChar + PARAM_DIR;
		this.expectedDir = workingDir + File.separatorChar + EXPECTED_DIR;
	}

	public boolean runScript() {
		// Create temporal directory
		final File tmp = new File(outputDir);

		try {
			deleteDirectory(tmp);
		} catch (final IOException e) {
			e.printStackTrace();
		}

		if (!tmp.mkdir())
			System.out.println("Could not create directory " + tmp.getAbsolutePath());

		final NS2Simulation ns2Simulation = new NS2Simulation();
		return ns2Simulation.runScript(workingDir, script, outputDir, new SaveOutputDirAction(outputDir));
	}
	
	class SaveOutputDirAction implements InterruptionAction {
		
		private final String outputDir;
		
		public SaveOutputDirAction(final String outputDir) {
			this.outputDir = outputDir;
		}

		@Override
		public void perform() throws Exception {
			File wDir = new File(workingDir);
			File tempDir = new File(System.getProperty("java.io.tmpdir") + File.pathSeparatorChar + wDir.getName() + "-" + System.currentTimeMillis());
			tempDir.mkdir();
			
			File oDir = new File(outputDir);
			FileUtils.copyDirectory(oDir, tempDir);
		}
		
	}

	public void finish() {
		if (!outputDir.equals(""))
			try {
				deleteDirectory(new File(outputDir));
			} catch (final IOException e) {
				e.printStackTrace();
			}
	}

	private static boolean deleteDirectory(final File path) throws IOException {
		if (path.exists()) {
			final File[] files = path.listFiles();
			for (int i = 0; i < files.length; i++)
				if (files[i].isDirectory())
					deleteDirectory(files[i]);
				else if (!files[i].delete())
					throw new IOException("Could not delete file " + files[i].getAbsolutePath());
		}
		return (path.delete());
	}
}
