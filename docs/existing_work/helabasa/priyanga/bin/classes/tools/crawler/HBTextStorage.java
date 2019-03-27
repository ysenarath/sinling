/**
 * @author Rajith Priyanga (c) 2013 - rpriyanga@yahoo.com 
 * 
 * 
 */
package helabasa.tools.crawler;

import java.io.BufferedWriter;
import java.io.FileWriter;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.Map;
import java.util.Map.Entry;

//Singleton
public class HBTextStorage 
{

	private Map<String, HBTextItem> map_Texts = new HashMap<String, HBTextItem>();
	
	public HBTextStorage() {
		// TODO Auto-generated constructor stub
	}
	
	synchronized public void AddText(String sItem, short iType)
	{
		HBTextItem oItem = GetTextItem(sItem, iType);
		oItem.AddOccurance();
	}
	
	public HBTextItem GetTextItem(String sItem, short iType)
	{
		HBTextItem oItem = map_Texts.get(sItem);
		if(oItem==null)
		{
			oItem = new HBTextItem(sItem, iType);			
		}
		return oItem;
	}
	
	public void Flush(int iType)
	{		
		long lCount = 0;
		
		for (Map.Entry<String, HBTextItem> e : map_Texts.entrySet())
		{	
			if(e.getValue().GetType()==iType)
			{
				lCount ++;
				
				HBSinhalaCrawler.AddToOutputFile(e.getKey() + "|" + e.getValue().GetCount());
			}
		}	
		
		System.out.println(HBSinhalaCrawler.GetTimeStamp() + " : HBC : " + lCount + " entries added. (Type=" + iType + ")");
	}
	
	public void Flush()
	{
		long lCount = 0;
		for (Map.Entry<String, HBTextItem> e : map_Texts.entrySet())
		{		    
			lCount ++;
		    HBSinhalaCrawler.AddToOutputFile(e.getKey() + "|" + e.getValue().GetCount());
		}
		
		System.out.println(HBSinhalaCrawler.GetTimeStamp() + " : HBC : " + lCount + " entries added.");
	}

}
