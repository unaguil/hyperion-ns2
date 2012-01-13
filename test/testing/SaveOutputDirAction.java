package testing;

import java.io.File;

import org.apache.commons.io.FileUtils;

class SaveOutputDirAction implements InterruptionAction {
	
	private final String outputDir;
	
	public SaveOutputDirAction(final String outputDir) {
		this.outputDir = outputDir;
	}

	@Override
	public void perform() throws Exception {
		File wDir = new File(outputDir);
		File tempDir = new File(System.getProperty("java.io.tmpdir") + File.separatorChar + wDir.getName() + "-" + System.currentTimeMillis());
		tempDir.mkdir();
		
		File oDir = new File(outputDir);
		FileUtils.copyDirectory(oDir, tempDir);
	}
	
}
