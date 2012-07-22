//
//  MMViewController.h
//  MagicMirror
//
//  Created by Doug Feigelson on 7/21/12.
//  Copyright (c) 2012 MIT. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <AVFoundation/AVFoundation.h>
#import <RestKit/RestKit.h>

@interface MMViewController : UIViewController <AVAudioRecorderDelegate, RKRequestDelegate> {
    NSString* recordingFilePath;
}

@property AVAudioRecorder* recorder; 
@property UIWebView* webView;

@end
