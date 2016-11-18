package confignow;

import java.lang.System;
import java.io.Console;

public class InputPrompter {

  public InputPrompter() {
    super();
  }

  public static String readPassword(String prompt) throws Exception {

    char[] passwd;
    Console cons;

    if ((prompt == null) || (prompt.length() == 0)) {
      prompt = "Enter Password:";
    }

    String text = null;
    cons = System.console();
    if (cons != null)
    {
        passwd = cons.readPassword("[%s]", prompt);
        if (passwd != null) {
          text = new String(passwd);
        }
    }
    
    return text;
  }
}

