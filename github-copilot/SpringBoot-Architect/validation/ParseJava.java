import com.sun.source.util.JavacTask;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.List;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

/** Solo análisis sintáctico (sin resolver tipos) de cada fichero listado en args[0]. */
public class ParseJava {
    public static void main(String[] args) throws Exception {
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        try (StandardJavaFileManager fm = compiler.getStandardFileManager(null, null, null)) {
            for (String file : Files.readAllLines(Path.of(args[0]))) {
                DiagnosticCollector<JavaFileObject> diags = new DiagnosticCollector<>();
                JavacTask task = (JavacTask) compiler.getTask(null, fm, diags,
                        List.of("-proc:none", "-encoding", "UTF-8"), null, fm.getJavaFileObjects(file));
                task.parse();
                String first = diags.getDiagnostics().stream()
                        .filter(d -> d.getKind() == Diagnostic.Kind.ERROR)
                        .findFirst()
                        .map(d -> d.getMessage(null).replace('\n', ' ') + " @" + d.getLineNumber())
                        .orElse("");
                System.out.println(file + "\t" + (first.isEmpty() ? "OK" : first));
            }
        }
    }
}
